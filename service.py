import pandas as pd
from functools import cmp_to_key
from itertools import chain

class BrandNew:
    def __init__(self, preference):
        self.preference = preference

    def pop_preference(self):
        return None if len(self.preference) == 0 else self.preference.pop(0)

class Department:
    def __init__(self, preference, capacity):
        self.preference = preference
        self.capacity = capacity
        self.__this_step_applicants = []
        self.__keep_members = []

    @property
    def keep_members(self):
        return self.__keep_members

    @keep_members.setter
    def this_step_applicant(self, value):
        self.__this_step_applicants = value
        combined = self.__keep_members + self.__this_step_applicants
        self.__keep_members = sorted(combined, key=cmp_to_key(self._compare_bn))[:self.capacity]
        self.__this_step_applicants = []

    def _compare_bn(self, arg1, arg2):
        return self.preference.index(arg1) - self.preference.index(arg2)

def run_matching(applicant_csv, host_csv):
    applicant_table = pd.read_csv(applicant_csv)
    host_table = pd.read_csv(host_csv)

    students = applicant_table.iloc[:, 0].values
    hosts = host_table.iloc[:, 0].values.tolist()

    preference = [pre + list(set(hosts) - set(pre)) for pre in applicant_table.iloc[:, 1:4].values.tolist()]
    brand_news = {sid: BrandNew(pref) for sid, pref in zip(applicant_table.iloc[:, 0], preference)}

    selection = [[x for x in pre_sel if pd.notnull(x)] + list(set(students) - set(pre_sel)) for pre_sel in host_table.iloc[:, 2:len(students)+2].values.tolist()]
    departments = {did: Department(sel, cap) for did, sel, cap in zip(hosts, selection, host_table.iloc[:, 1])}

    for _ in range(3):
        not_matched = set(brand_news.keys()) - set(chain.from_iterable(dept.keep_members for dept in departments.values()))
        if not not_matched:
            break
        for x in not_matched:
            target_dept = brand_news[x].pop_preference()
            if target_dept:
                departments[target_dept].this_step_applicant = [x]

    decision = [[host] + sorted(dept.keep_members) for host, dept in departments.items()]
    unmatch_list = list(set(students) - set(chain.from_iterable(decision)))

    decided = pd.DataFrame(decision)
    unmatch = pd.DataFrame(unmatch_list)

    decided.to_csv("decided_students.csv", index=None)
    unmatch.to_csv("unmatched_students.csv", index=None)
    return "Matching completed."
