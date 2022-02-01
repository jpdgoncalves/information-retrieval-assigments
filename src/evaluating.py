import re
import time
from math import log2
from statistics import mean, median
from typing import Callable


class Evaluator:
    def __init__(
            self, queries_rev_path: str,
            search_func: Callable[[str, int], list[tuple[str, float]]],
            results_limit=100
    ):
        self.queries_rev = read_relevance_file(queries_rev_path)
        self.precisions = []
        self.recalls = []
        self.f_measures = []
        self.avg_precisions = []
        self.ndgcs = []
        self.query_times = []
        self.search_func = search_func
        self.results_limit = results_limit

    def search(self, query: str):
        print(f"[Evaluator]: searching '{query}'")
        start = time.time()
        results = self.search_func(query, self.results_limit)
        end = time.time()

        print(f"[Evaluator]: Registering results for '{query}'")
        precision = self.calc_precision(query, results)
        recall = self.calc_recall(query, results)
        f_measure = (2 * recall * precision) / (recall + precision)
        avg_precision = self.calc_avg_precision(query, results)
        ndgc = self.calc_ndgc(query, results)

        self.precisions.append(precision)
        self.recalls.append(recall)
        self.f_measures.append(f_measure)
        self.avg_precisions.append(avg_precision)
        self.ndgcs.append(ndgc)
        self.query_times.append(end - start)
        return results

    def calc_precision(self, query: str, results: list[tuple[str, float]]):
        n_results = len(results)
        n_t_results = self.calc_n_true_results(query, results)

        return n_t_results / n_results

    def calc_recall(self, query: str, results: list[tuple[str, float]]):
        n_t_results = self.calc_n_true_results(query, results)
        expected_results = self.queries_rev[query]
        n_expected_res = len(expected_results)

        return n_t_results / n_expected_res

    def calc_avg_precision(self, query: str, results: list[tuple[str, float]]):
        expected_results = self.queries_rev[query]
        n_t_results = 0
        precisions = []

        for i, (review_id, _) in enumerate(results, start=1):
            if review_id in expected_results:
                n_t_results += 1
                precisions.append(n_t_results / i)

        return mean(precisions)

    def calc_ndgc(self, query: str, results: list[tuple[str, float]]):
        return self.calc_dgc(query, results) / self.calc_perf_dgc(query)

    def calc_dgc(self, query: str, results: list[tuple[str, float]]):
        expected_results = self.queries_rev[query]
        (first_r_id, _), *rem_results = results
        dgc = expected_results[first_r_id] if first_r_id in expected_results else 0

        for i, (review_id, _) in enumerate(rem_results, start=2):
            if review_id in expected_results:
                dgc += expected_results[review_id] / log2(i)

        return dgc

    def calc_perf_dgc(self, query: str):
        expected_results = self.queries_rev[query]
        exp_res_iter = expected_results.items()
        _, dgc = next(exp_res_iter)

        for i, (_, relevance) in zip(range(2, self.results_limit), exp_res_iter):
            dgc += relevance / log2(i)

        return dgc

    def calc_n_true_results(self, query: str, results: list[tuple[str, float]]):
        expected_results = self.queries_rev[query]
        n_t_results = 0

        for review_id, _ in results:
            if review_id in expected_results:
                n_t_results += 1

        return n_t_results

    def output_evaluation(self, dest_path: str):
        print(f"[Evaluator]: Writing evaluation results to '{dest_path}'")

        with open(dest_path, "w", newline="\n", encoding="utf-8") as dest_f:
            dest_f.write(f"Evaluation results for top {self.results_limit}\n\n\n")
            dest_f.write(f"Mean Precision: {mean(self.precisions)}\n")
            dest_f.write(f"Mean Recall: {mean(self.recalls)}\n")
            dest_f.write(f"Mean F-Measure: {mean(self.f_measures)}\n")
            dest_f.write(f"Mean Average Precision: {mean(self.avg_precisions)}\n")
            dest_f.write(f"Mean NDCG: {mean(self.ndgcs)}\n")

            query_throughout = len(self.query_times) / sum(self.query_times)
            query_median = median(sorted(self.query_times))

            dest_f.write(f"Query Throughout: {query_throughout}/s\n")
            dest_f.write(f"Query Median: {query_median}s\n\n\n")


def read_relevance_file(f_path: str) -> dict[str, dict[str, int]]:
    rel_line_parse = relevance_line_parser()
    parsed_data = {}

    with open(f_path, newline="\n") as relevance_file:
        while True:
            query = relevance_file.readline().strip()

            if len(query) == 0:
                break
            else:
                query = query[2:]

            parsed_data[query] = {}
            expected_result = relevance_file.readline()
            while expected_result != "\n":
                review_id, relevance = rel_line_parse(expected_result)
                parsed_data[query][review_id] = relevance
                expected_result = relevance_file.readline()

        return parsed_data


def relevance_line_parser():
    space_tabs_matcher = re.compile("[ \t][ \t]*")

    def parse_line(line: str):
        line = line.strip()
        line = space_tabs_matcher.sub(" ", line)
        review_id, relevance = line.split(" ")
        return review_id, int(relevance)

    return parse_line
