import concurrent.futures
import itertools
import math
import random
import sys

import numpy as np
import pandas as pd

# import time


class Landscape:
    def __init__(self, smoothness, length=10):

        self.s = smoothness
        self.length = length

        """Generate landscape heights"""
        total_segments = round(self.length / self.s)
        points = [random.choice(range(1, 101))]  # points that define landscape
        heights = []  # full landscape

        for j in range(total_segments - 1):
            a = points[-1]
            b = random.choice(range(1, 101))  # new random point to define landscape
            points.append(b)
            seg_len = random.choice(range(1, 2 * self.s))
            """Fill in locations between two points"""
            step = np.round((b - a) / seg_len, 2)
            for i in range(1, seg_len + 1):
                if a + step * i > 100:
                    heights.append(100)
                else:
                    heights.append(a + step * i)

        self.heights = heights
        self.length = len(self.heights)


class Agent:
    def __init__(self, no, h, landscape, sigma=0):
        self.no = no  # Agent ID
        self.h = h  # Ordered list of step sizes
        self.landscape = landscape
        self.score = 0  # Highest value found
        self.sigma = sigma  # Level of noise in signals

    def data(self, loc):
        """Get noisy data from location"""
        return max(np.random.normal(self.landscape.heights[loc], self.sigma), 0.001)

    def search(self, start, own_hist, in_hist):
        """own_hist records agent's own search results"""
        """in_hist records known results by the ingroup"""
        start = start  # Starting location on landscape
        loc = start  # Current location
        findings = own_hist
        if in_hist[loc] == 0:
            """Starting loc hasn't been searched by ingroup members"""
            value = self.data(loc)
            findings[loc], maxi = value, value
        else:
            """Starting loc has been searched by ingroup members"""
            maxi = in_hist[loc]  # Current max value found

        count = 0  # Number of step sizes tried
        n_total = 0

        while count < len(self.h):
            nxt = (
                loc + self.h[n_total % 3]
            ) % self.landscape.length  # Next loc to check
            if in_hist[nxt] == 0:
                """Never checked by ingroup"""
                value = self.data(nxt)
                findings[nxt], in_hist[nxt] = value, value
                if maxi < value:
                    """Found value higher than current one"""
                    loc, maxi, count = nxt, value, 0
                    n_total += 1
                else:
                    count += 1
                    n_total += 1
            else:
                """Loc already checked by self or ingroup"""
                value = in_hist[nxt]
                if maxi < value:
                    loc, maxi, count = nxt, value, 0
                    n_total += 1
                else:
                    count += 1
                    n_total += 1
        return findings


class Team:
    def __init__(self, members, landscape, trust_level=1):
        self.members = members
        self.landscape = landscape
        self.trust_level = trust_level  # Size of trusted subgroups
        self.trust = dict()
        for a in self.members:
            self.trust[a] = [a]
        if self.trust_level > 0:
            M = self.members
            random.shuffle(M)
            k = math.ceil(len(self.members) * self.trust_level)
            while len(M) > 0:
                subgroup = M[:k]
                M = M[k:]
                for b in subgroup:
                    self.trust[b] = subgroup

    def aggregate(self, maps):
        """Aggregate search results from multiple agents"""
        denom = np.sum([np.where(m > 0, 1, 0) for m in maps.values()], axis=0)
        num = np.sum([m for m in maps.values()], axis=0)
        return num / (denom + np.where(denom == 0, 1, 0))

    def tournament(self, start):
        maps = dict()  # Cumulative search results by members
        for a in self.members:
            maps[a] = np.array([0] * self.landscape.length)
        on = True
        maxi = 0  # Current max value found
        loc = start  # Location where current max value is found

        while on:
            for m in self.members:
                in_hist = np.sum([maps[n] for n in self.trust[m]], axis=0)
                maps[m] = m.search(loc, maps[m], in_hist)

            on = False
            new_max, new_loc = np.amax(self.aggregate(maps)), np.argmax(
                self.aggregate(maps)
            )
            if new_max > maxi:
                on = True  # Continue if higher value found in new round
                loc, maxi = new_loc, new_max

        return self.landscape.heights[np.argmax(self.aggregate(maps))]


poolsize = 9
pool = list(range(1, poolsize + 1))
h_each = 3  # Number of step sizes each agent has
per_team = 9  # Number of agents per team
all_perm = list(itertools.permutations(pool, r=h_each))  # All possible step size combo


def calc_score(a, L):
    """Calculate agent's avg search score from all starting points of landscape"""
    scores = []
    for i in range(L.length):
        np.random.seed()
        results = a.search(i, np.array([0] * L.length), np.array([0] * L.length))
        score = L.heights[np.argmax(results)]
        scores.append(score)
    a.score = np.mean(scores)


def find_experts(L, t):
    """Returns agents with top individual search scores"""
    agents = []  # all possible heuristic profiles
    for i in range(len(all_perm)):
        a = Agent(i, all_perm[i], L, sigma=0)
        agents.append(a)
    if __name__ == "__main__":
        with concurrent.futures.ThreadPoolExecutor() as executor:
            r = [executor.submit(calc_score, a, L) for a in agents]
    agents.sort(key=lambda x: x.score, reverse=True)  # sort agents by expertise
    return Team(agents[:per_team], L, trust_level=t)


def tournament(team, i):
    np.random.seed()
    return team.tournament(i)


def run(s, t, sigma=8):
    # cols = [
    #     "smoothness",
    #     "diverse",
    #     "expert",
    #     "d_heuristics",
    #     "x_heuristics",
    #     "trust",
    #     "sigma",
    #     "poolsize",
    # ]
    # df = pd.DataFrame(columns=cols)

    L = Landscape(s)

    expert = find_experts(L, t)
    for e in expert.members:
        e.sigma = sigma

    d_heu = random.sample(all_perm, per_team)  # Randomly generate diverse group
    diverse = Team(
        [Agent(i + len(all_perm), d_heu[i], L, sigma) for i in range(per_team)],
        L,
        trust_level=t,
    )
    d_record = []
    x_record = []

    if __name__ == "__main__":
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(tournament, diverse, i) for i in range(L.length)]

            for f in concurrent.futures.as_completed(results):
                d_record.append(f.result())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(tournament, expert, i) for i in range(L.length)]

            for f in concurrent.futures.as_completed(results):
                x_record.append(f.result())

    data = [
        L.s,
        np.mean(d_record),
        np.mean(x_record),
        list(itertools.chain.from_iterable([a.h for a in diverse.members])),
        list(itertools.chain.from_iterable([a.h for a in expert.members])),
        t,
        sigma,
        poolsize,
    ]

    # df = pd.concat(
    #     [
    #         df,
    #         pd.DataFrame(
    #             data,
    #             columns=cols,
    #         ),
    #     ],
    #     ignore_index=True,
    # )
    return data
    # df.to_csv("data.csv", index=False)


class Simulation:
    def __init__(self, Smoothness: list, Sigma: list, Trust: list) -> None:
        self.Smoothness = Smoothness
        self.Sigma = Sigma
        self.Trust = Trust
        self.grid = [
            (s, t, sigma)
            for s in self.Smoothness
            for t in self.Trust
            for sigma in self.Sigma
        ]

    def simulation(self):
        cols = [
            "smoothness",
            "diverse",
            "expert",
            "d_heuristics",
            "x_heuristics",
            "trust",
            "sigma",
            "poolsize",
        ]
        df = pd.DataFrame(columns=cols)

        for k, (s, t, sigma) in enumerate(self.grid):
            df.loc[k] = run(s, t, sigma)

        return df


if __name__ == "__main__":
    Smoothness = range(1, 9)
    Sigma = [0]
    # Sigma = [0, 4, 8, 12]
    Trust = [1]
    # Trust = [0, 0.33, 0.5, 1]
    Simulation(Smoothness, Sigma, Trust).simulation().to_csv("data/landscape.csv")

    # if len(sys.argv) != 4:
    #     print("error")
    #     sys.exit(1)

    # s = int(sys.argv[1])
    # t = float(sys.argv[2])
    # sigma = float(sys.argv[3])
    # run(s, t, sigma)
