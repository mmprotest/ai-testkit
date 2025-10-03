"""JUnit report serialization."""
from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from ..runners.dataset_runner import RunReport


class JUnitReport:
    def __init__(self, root: Element) -> None:
        self.root = root

    @classmethod
    def from_run(cls, report: RunReport, timestamp: str) -> "JUnitReport":
        testsuite = Element("testsuite", attrib={
            "name": report.suite.name,
            "tests": str(len(report.cases)),
            "timestamp": timestamp,
        })
        for case in report.cases:
            testcase = SubElement(testsuite, "testcase", attrib={"name": case.name})
            if not case.passed:
                failure = SubElement(testcase, "failure", attrib={"message": "Failed"})
                failure.text = case.output
        return cls(testsuite)

    def to_xml(self) -> str:
        return tostring(self.root, encoding="unicode")

