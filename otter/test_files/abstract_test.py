"""Abstract test objects for providing a schema to write and parse test cases"""

import random
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, replace
from textwrap import indent
from typing import Optional, Union


OK_FORMAT_VARNAME = "OK_FORMAT"


# # class for storing the test cases themselves
# #   - body is the string that gets run for the test
# #   - hidden is the visibility of the test case
# #   - points is the number of points this test case is worth
# TestCase = namedtuple("TestCase", ["name", "body", "hidden", "points", "success_message", "failure_message"])

@dataclass
class TestCase:

    name: str

    body: str

    hidden: bool

    points: Union[int, float]

    success_message: Optional[str]

    failure_message: Optional[str]


@dataclass
class TestCaseResult:

    test_case: TestCase

    message: Optional[str]

    passed: bool

# # class for storing the results of a single test _case_ (within a test file)
# #   - message should be a string to print out to the student (ignored if passed is True)
# #   - passed is whether the test case passed
# #   - hidden is the visibility of the test case
# TestCaseResult = namedtuple("TestCaseResult", ["test_case", "message", "passed"])


class TestFile(ABC):
    """
    A (abstract) single test file for Otter. This ABC defines how test results are represented and sets
    up the instance variables tracked by tests. Subclasses should implement the abstract class method
    ``from_file`` and the abstract instance method ``run``.

    Args:
        name (``str``): the name of test file
        path (``str``): the path to the test file
        test_cases (``list`` of ``TestCase``): a list of parsed tests to be run
        all_or_nothing (``bool``, optional): whether the test should be graded all-or-nothing across
            cases

    Attributes:
        name (``str``): the name of test file
        path (``str``): the path to the test file
        test_cases (``list`` of ``TestCase``): a list of parsed tests to be run
        all_or_nothing (``bool``): whether the test should be graded all-or-nothing across
            cases
        test_case_results (``list`` of ``TestCaseResult``): a list of results for the test cases in
            ``test_cases``
    """

    # def _repr_html_(self):
    #     if self.passed_all:
    #         all_passed_emoji = random.choice(['🍀', '🎉', '🌈', '🙌', '🚀', '🌟', '✨', '💯'])
    #         if any(tcr.test_case.success_message is not None for tcr in self.test_case_results):
    #             ret = f"<p><strong><pre style='display: inline;'>{self.name}</pre></strong> passed! {all_passed_emoji}</p>"
    #             for tcr in self.test_case_results:
    #                 if tcr.test_case.success_message is not None:
    #                     ret += f"<p><strong><pre style='display: inline;'>{tcr.test_case.name}</pre> message:</strong> {tcr.test_case.success_message}</p>"
    #             return ret
    #         return f"<p><strong><pre style='display: inline;'>{self.name}</pre></strong> passed! {all_passed_emoji}</p>"
    #     else:
    #         ret = f"<p><strong style='color: red;'><pre style='display: inline;'>{self.name}</pre> results:</strong></p>"
    #         for tcr in self.test_case_results:
    #             if tcr.passed and tcr.test_case.success_message is not None:
    #                 ret += f"<p><strong><pre style='display: inline;'>{tcr.test_case.name}</pre> message:</strong> {tcr.test_case.success_message}</p>"
    #             if not tcr.passed and tcr.test_case.failure_message is not None:
    #                 ret += f"<p><strong><pre style='display: inline;'>{tcr.test_case.name}</pre> message:</strong> {tcr.test_case.failure_message}</p>"
    #             ret += f"<p><strong><pre style='display: inline;'>{tcr.test_case.name}</pre> result:</strong></p>"
    #             ret += f"<pre>{indent(tcr.message, '    ')}</pre>"

    #         return ret

    def _repr_html_(self):
        ret = f"<strong><p><pre style='display: inline;'>{self.name}</pre> results:</p>"
        ret += '<font color=\"#a03196\"><ul style="list-style: none;">'
        for tcr in self.test_case_results:
            if tcr.passed:
                ret += f"<li>✅ <samp>{tcr.test_case.body[4:]}<samp></li>"
            else:
                message = tcr.message
                if "\nGot:\n" in message:
                    output_index = message.index("\nGot:\n")
                    message = message[(output_index + len("\nGot:\n")):]
                elif "\nException raised:\n" in message:
                    output_index = message.index("\nException raised:\n")
                    #message = message[(output_index + len("\nException raised:\n")):]
                    message = message.strip().split('\n')[-1]
                ret += f'<li>❌ <samp>{tcr.test_case.body[4:]}<samp><pre style="color:#a03196;">{indent(message.strip(), "      ")}</pre></li>\n'

        return ret + "</ul></font></strong>"

    def __repr__(self):
        ret = "" # "\u001b[35m\u001b[1m\n"
        for tcr in self.test_case_results:
            if tcr.passed:
                ret += f"✅ {tcr.test_case.body[4:]}"
            else:
                message = tcr.message
                if "\nGot:\n" in message:
                    output_index = message.index("\nGot:\n")
                    message = message[(output_index + len("\nGot:\n")):]
                elif "\nException raised:\n" in message:
                    output_index = message.index("\nException raised:\n")
                    message = message.strip().split('\n')[-1]
                ret += f"\n❌ {tcr.test_case.body[4:]}{indent(message.strip(), '      ')}\n"
        return ret # + "\u001b[0m"

    # @abstractmethod
    def __init__(self, name, path, test_cases, all_or_nothing=True):
        self.name = name
        self.path = path
        self.test_cases = test_cases
        self.all_or_nothing = all_or_nothing
        self.test_case_results = []
        self._score = None

    @staticmethod
    def resolve_test_file_points(total_points, test_cases):
        if isinstance(total_points, list):
            if len(total_points) != len(test_cases):
                raise ValueError("Points specified in test has different length than number of test cases")
            test_cases = [replace(tc, points=pt) for tc, pt in zip(test_cases, total_points)]
            total_points = None

        elif total_points is not None and not isinstance(total_points, (int, float)):
            raise TypeError(f"Test spec points has invalid type: {total_points}")

        point_values = []
        for i, test_case in enumerate(test_cases):
            if test_case.points is not None:
                assert type(test_case.points) in (int, float), f"Invalid point type: {type(test_case.points)}"
                point_values.append(test_case.points)

            else:
                point_values.append(None)

        pre_specified = sum(p for p in point_values if p is not None)
        if total_points is not None:
            if pre_specified > total_points:
                raise ValueError(f"More points specified in test cases that allowed for test")

            else:
                try:
                    per_remaining = (total_points - pre_specified) / sum(1 for p in point_values if p is None)
                except ZeroDivisionError:
                    per_remaining = 0.0

        else:
            if pre_specified == 0 and all(p in (0, None) for p in point_values):
                # if only zeros specified, assume test worth 1 pt and divide amongst nonzero cases
                try:
                    per_remaining = 1 / sum(p is None for p in point_values)
                except ZeroDivisionError:
                    per_remaining = 0.0

            elif pre_specified == 0:
                per_remaining = 1 / len(point_values)

            else:
                # assume all other tests are worth 0 points
                per_remaining = 0.0

        point_values = [p if p is not None else per_remaining for p in point_values]
        return [replace(tc, points=p) for tc, p in zip(test_cases, point_values)]

    @property
    def passed_all(self):
        return all(tcr.passed for tcr in self.test_case_results)

    @property
    def passed_all_public(self):
        return all(tcr.passed for tcr in self.test_case_results if not tcr.test_case.hidden)

    @property
    def all_public(self):
        return all(not tc.hidden for tc in self.test_cases)

    @property
    def grade(self):
        if self.all_or_nothing and not self.passed_all:
            return 0
        elif self.all_or_nothing and self.passed_all:
            return 1
        else:
            return sum(tcr.test_case.points for tcr in self.test_case_results if tcr.passed) / \
                sum(tc.points for tc in self.test_cases)

    @property
    def score(self):
        if self._score is not None:
            return self._score
        return sum(tcr.test_case.points for tcr in self.test_case_results if tcr.passed)

    @property
    def possible(self):
        return sum(tc.points for tc in self.test_cases)

    def update_score(self, new_score):
        self._score = new_score

    def to_dict(self):
        return {
            "score": self.score,
            "possible": self.possible,
            "name": self.name,
            "path": self.path,
            "test_cases": [asdict(tc) for tc in self.test_cases],
            "all_or_nothing": self.all_or_nothing,
            "test_case_results": [asdict(tcr) for tcr in self.test_case_results],
        }
    
    def summary(self, public_only=False):
        if (not public_only and self.passed_all) or (public_only and self.passed_all_public):
            ret = f"\u001b[1m{self.name} results:\n    ✅ All test cases passed!\u001b[0m"
            if (not public_only and self.passed_all) and \
                    any(tcr.test_case.success_message is not None for tcr in self.test_case_results):
                for tcr in self.test_case_results:
                    if tcr.test_case.success_message is not None:
                        ret += f"\n{tcr.test_case.name} message: {tcr.test_case.success_message}"
            return ret

        tcrs = self.test_case_results
        if public_only:
            tcrs = [tcr for tcr in tcrs if not tcr.test_case.hidden]

        tcr_summaries = []
        for tcr in tcrs:
            if not tcr.passed:
                message = tcr.message
                if "\nGot:\n" in message:
                    output_index = message.index("\nGot:\n")
                    message = message[(output_index + len("\nGot:\n")):]
                elif "\nException raised:\n" in message:
                    output_index = message.index("\nException raised:\n")
                    message = message.strip().split('\n')[-1]
                smry = f"\u001b[35m\u001b[1m❌ {tcr.test_case.body[4:]}{indent(message.strip(), '      ')}\u001b[0m"
                tcr_summaries.append(smry.strip())

        return f"\u001b[1m{self.name} results:\u001b[0m\n" + indent("\n\n".join(tcr_summaries), "    ")



    # def summary(self, public_only=False):
    #     if (not public_only and self.passed_all) or (public_only and self.passed_all_public):
    #         ret = f"{self.name} results: All test cases passed!"
    #         if (not public_only and self.passed_all) and \
    #                 any(tcr.test_case.success_message is not None for tcr in self.test_case_results):
    #             for tcr in self.test_case_results:
    #                 if tcr.test_case.success_message is not None:
    #                     ret += f"\n{tcr.test_case.name} message: {tcr.test_case.success_message}"
    #         return ret

    #     tcrs = self.test_case_results
    #     if public_only:
    #         tcrs = [tcr for tcr in tcrs if not tcr.test_case.hidden]

    #     tcr_summaries = []
    #     for tcr in tcrs:
    #         smry = ""
    #         if tcr.passed and tcr.test_case.success_message is not None:
    #             smry += f"{tcr.test_case.name} message: {tcr.test_case.success_message}\n\n"
    #         if not tcr.passed and tcr.test_case.failure_message is not None:
    #             smry += f"{tcr.test_case.name} message: {tcr.test_case.failure_message}\n\n"
    #         smry += f"{tcr.test_case.name} result:\n"
    #         smry += f"{indent(tcr.message.strip(), '    ')}\n\n"

    #         tcr_summaries.append(smry.strip())

    #     return f"{self.name} results:\n" + indent("\n\n".join(tcr_summaries), "    ")

    @classmethod
    @abstractmethod
    def from_file(cls, path):
        ...

    @abstractmethod
    def run(self, global_environment):
        ...
