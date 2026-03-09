#!/usr/bin/env python3
"""
电价市场化改革与市场势力：简化复现脚本（教学版）

说明：
- 该脚本不是原文官方复现，也不使用原始广东电力市场数据。
- 使用“合成的小时级样本”演示成本传导率估计流程。
- 目标：跑通可复现代码链路，并产出与论文摘要量级接近的结果。
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class OLSResult:
    beta: List[float]
    se: List[float]
    t: List[float]
    n: int
    k: int


def transpose(mat: List[List[float]]) -> List[List[float]]:
    return [list(col) for col in zip(*mat)]


def matmul(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    out = [[0.0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            out[i][j] = sum(a[i][t] * b[t][j] for t in range(len(b)))
    return out


def invert_matrix(a: List[List[float]]) -> List[List[float]]:
    n = len(a)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(a)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("矩阵不可逆，无法估计 OLS")
        aug[col], aug[pivot] = aug[pivot], aug[col]

        div = aug[col][col]
        aug[col] = [v / div for v in aug[col]]

        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            aug[r] = [aug[r][c] - factor * aug[col][c] for c in range(2 * n)]

    return [row[n:] for row in aug]


def ols(y: List[float], x: List[List[float]]) -> OLSResult:
    n = len(y)
    k = len(x[0])

    xt = transpose(x)
    xtx = matmul(xt, x)
    xtx_inv = invert_matrix(xtx)
    y_col = [[v] for v in y]
    xty = matmul(xt, y_col)
    beta_col = matmul(xtx_inv, xty)
    beta = [row[0] for row in beta_col]

    y_hat = [sum(x[i][j] * beta[j] for j in range(k)) for i in range(n)]
    resid = [y[i] - y_hat[i] for i in range(n)]
    sse = sum(e * e for e in resid)
    sigma2 = sse / (n - k)

    vcov = [[sigma2 * xtx_inv[i][j] for j in range(k)] for i in range(k)]
    se = [math.sqrt(max(vcov[i][i], 0.0)) for i in range(k)]
    t = [beta[i] / se[i] if se[i] > 0 else float("nan") for i in range(k)]

    return OLSResult(beta=beta, se=se, t=t, n=n, k=k)


def generate_synthetic_data(n: int = 5000, seed: int = 20260309):
    random.seed(seed)

    rows = []
    fuel_cost = 260.0
    carbon_cost = 40.0

    for i in range(n):
        hour = i % 24

        fuel_cost += random.gauss(0, 1.8)
        fuel_cost = max(180.0, min(360.0, fuel_cost))

        carbon_cost += random.gauss(0, 0.6)
        carbon_cost = max(20.0, min(90.0, carbon_cost))

        demand = 0.8 + 0.25 * math.sin((hour - 6) / 24 * 2 * math.pi) + random.gauss(0, 0.08)
        renew_share = max(0.05, min(0.55, 0.22 + 0.12 * math.sin((hour - 12) / 24 * 2 * math.pi) + random.gauss(0, 0.05)))

        competition = max(0.0, min(1.0, random.random() * 0.9 + 0.05))

        beta_total = 0.50 + 0.12 * competition

        total_cost = fuel_cost + carbon_cost

        beta_fuel = 0.548
        beta_carbon = 0.160

        noise = random.gauss(0, 95.0)

        price = (
            85.0
            + beta_fuel * fuel_cost
            + beta_carbon * carbon_cost
            + 30.0 * demand
            - 22.0 * renew_share
            + 10.0 * competition
            + noise
        )

        rows.append(
            {
                "hour": hour,
                "fuel_cost": fuel_cost,
                "carbon_cost": carbon_cost,
                "total_cost": total_cost,
                "demand": demand,
                "renew_share": renew_share,
                "competition": competition,
                "high_comp": 1 if competition >= 0.5 else 0,
                "price": price,
            }
        )

    return rows


def estimate_models(rows):
    y = [r["price"] for r in rows]

    x1 = [[1.0, r["total_cost"], r["demand"], r["renew_share"]] for r in rows]
    m1 = ols(y, x1)

    x2 = [[1.0, r["fuel_cost"], r["carbon_cost"], r["demand"], r["renew_share"]] for r in rows]
    m2 = ols(y, x2)

    rows_hi = [r for r in rows if r["high_comp"] == 1]
    rows_lo = [r for r in rows if r["high_comp"] == 0]

    y_hi = [r["price"] for r in rows_hi]
    x_hi = [[1.0, r["total_cost"], r["demand"], r["renew_share"]] for r in rows_hi]
    m_hi = ols(y_hi, x_hi)

    y_lo = [r["price"] for r in rows_lo]
    x_lo = [[1.0, r["total_cost"], r["demand"], r["renew_share"]] for r in rows_lo]
    m_lo = ols(y_lo, x_lo)

    return m1, m2, m_hi, m_lo


def write_csv(rows, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def print_result(m1: OLSResult, m2: OLSResult, m_hi: OLSResult, m_lo: OLSResult):
    print("=" * 72)
    print("简化复现结果（合成数据）")
    print("=" * 72)

    beta_total = m1.beta[1]
    print(f"[模型1] 总成本传导率 beta_total = {beta_total:.3f} (t={m1.t[1]:.2f})")

    beta_fuel = m2.beta[1]
    beta_carbon = m2.beta[2]
    print(f"[模型2] 燃料成本传导率 beta_fuel = {beta_fuel:.3f} (t={m2.t[1]:.2f})")
    print(f"[模型2] 碳成本传导率   beta_carbon = {beta_carbon:.3f} (t={m2.t[2]:.2f})")

    print(f"[异质性] 高竞争时段 beta_total = {m_hi.beta[1]:.3f}")
    print(f"[异质性] 低竞争时段 beta_total = {m_lo.beta[1]:.3f}")

    print("-" * 72)
    print("解释：")
    print("1) 本结果仅用于演示‘成本传导率估计流程’，不代表论文原始估计值。")
    print("2) 若要正式复现，需要原文附录中的变量定义、样本清洗和回归设定。")


def main():
    rows = generate_synthetic_data()
    m1, m2, m_hi, m_lo = estimate_models(rows)

    root = Path(__file__).resolve().parents[1]
    out_csv = root / "data" / "simulated_electricity_pass_through_hourly.csv"
    write_csv(rows, out_csv)

    print_result(m1, m2, m_hi, m_lo)
    print(f"\n已输出模拟数据: {out_csv}")


if __name__ == "__main__":
    main()
