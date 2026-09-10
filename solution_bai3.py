"""
Mô-đun đối soát và tính thù lao tài xế RikkeiExpress Logistics (TPS -> MIS)
Bài tập: IT105 Session 02 - Bài 3 (Vận dụng chuyên sâu)
"""

import json
from typing import List, Dict, Any

def calculate_driver_payout(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Tính thù lao tuần, tạm giữ đơn tranh chấp và cộng thưởng mốc cho tài xế RikkeiExpress từ dữ liệu TPS.
    
    Quy tắc nghiệp vụ:
    - Thù lao cơ bản: 20.000đ / đơn giao thành công (DELIVERED).
    - Tạm giữ: Đơn bị tranh chấp (DISPUTED) tạm giữ 20.000đ/đơn, không tính vào số đơn thành công.
    - Thưởng vượt mốc: > 50 đơn DELIVERED trong tuần thưởng thêm 10% tổng thù lao cơ bản.
    """
    BASE_RATE = 20000  # 20.000đ / đơn giao thành công
    BONUS_THRESHOLD = 50  # Vượt 50 đơn thành công (> 50)
    BONUS_PERCENTAGE = 0.10  # Thưởng 10% trên tổng thù lao cơ bản

    driver_summary: Dict[str, Dict[str, Any]] = {}

    for tx in transactions:
        driver_id = tx.get("driver_id")
        driver_name = tx.get("driver_name", f"Driver_{driver_id}")
        status = str(tx.get("status", "")).upper()
        tx_id = tx.get("transaction_id")

        if not driver_id:
            continue

        if driver_id not in driver_summary:
            driver_summary[driver_id] = {
                "driver_name": driver_name,
                "total_orders": 0,
                "delivered_orders": 0,
                "disputed_orders": 0,
                "cancelled_orders": 0,
                "disputed_tx_ids": [],
                "base_payout": 0,
                "held_payout": 0,
                "bonus_payout": 0,
                "net_payout": 0
            }

        stats = driver_summary[driver_id]
        stats["total_orders"] += 1

        if status == "DELIVERED":
            stats["delivered_orders"] += 1
        elif status == "DISPUTED":
            stats["disputed_orders"] += 1
            stats["disputed_tx_ids"].append(tx_id)
            stats["held_payout"] += BASE_RATE
        elif status == "CANCELLED":
            stats["cancelled_orders"] += 1

    for driver_id, stats in driver_summary.items():
        delivered_cnt = stats["delivered_orders"]
        base_payout = delivered_cnt * BASE_RATE
        stats["base_payout"] = base_payout

        if delivered_cnt > BONUS_THRESHOLD:
            bonus_payout = int(base_payout * BONUS_PERCENTAGE)
        else:
            bonus_payout = 0
        stats["bonus_payout"] = bonus_payout

        # Thực nhận = Thù lao cơ bản + Thưởng mốc (chưa gồm các đơn DISPUTED bị tạm giữ)
        stats["net_payout"] = base_payout + bonus_payout

    return driver_summary


if __name__ == "__main__":
    sample_tps_transactions = [
        # DRV001: 52 đơn DELIVERED, 2 đơn DISPUTED -> Đạt mốc > 50 đơn DELIVERED
        *[{"transaction_id": f"TX_1_{i}", "driver_id": "DRV001", "driver_name": "Nguyen Van A", "status": "DELIVERED"} for i in range(1, 53)],
        {"transaction_id": "TX_1_53", "driver_id": "DRV001", "driver_name": "Nguyen Van A", "status": "DISPUTED"},
        {"transaction_id": "TX_1_54", "driver_id": "DRV001", "driver_name": "Nguyen Van A", "status": "DISPUTED"},

        # DRV002: 50 đơn DELIVERED, 2 đơn DISPUTED -> Đúng 50 đơn, KHÔNG vượt mốc (> 50)
        *[{"transaction_id": f"TX_2_{i}", "driver_id": "DRV002", "driver_name": "Tran Van B", "status": "DELIVERED"} for i in range(1, 51)],
        {"transaction_id": "TX_2_51", "driver_id": "DRV002", "driver_name": "Tran Van B", "status": "DISPUTED"},
        {"transaction_id": "TX_2_52", "driver_id": "DRV002", "driver_name": "Tran Van B", "status": "DISPUTED"},
        {"transaction_id": "TX_2_53", "driver_id": "DRV002", "driver_name": "Tran Van B", "status": "CANCELLED"},

        # DRV003: 48 đơn DELIVERED, 5 đơn DISPUTED -> 48 đơn -> Không đạt mốc
        *[{"transaction_id": f"TX_3_{i}", "driver_id": "DRV003", "driver_name": "Le Van C", "status": "DELIVERED"} for i in range(1, 49)],
        *[{"transaction_id": f"TX_3_DISP_{i}", "driver_id": "DRV003", "driver_name": "Le Van C", "status": "DISPUTED"} for i in range(1, 6)],
    ]

    payout_report = calculate_driver_payout(sample_tps_transactions)

    print("=" * 92)
    print(" BÁO CÁO TỔNG CƯỚC THÙ LAO TÀI XẾ RIKKEIEXPRESS (MIS REPORT) ".center(92, "="))
    print("=" * 92)
    
    header = f"{'ID':<8} | {'Tên tài xế':<15} | {'Đã giao':<8} | {'Tranh chấp':<10} | {'Thù lao CB':<12} | {'Tạm giữ':<10} | {'Thưởng 10%':<10} | {'Thực nhận':<12}"
    print(header)
    print("-" * 92)

    for drv_id, report in payout_report.items():
        print(f"{drv_id:<8} | "
              f"{report['driver_name']:<15} | "
              f"{report['delivered_orders']:<8} | "
              f"{report['disputed_orders']:<10} | "
              f"{report['base_payout']:>10,}đ | "
              f"{report['held_payout']:>8,}đ | "
              f"{report['bonus_payout']:>8,}đ | "
              f"{report['net_payout']:>10,}đ")

    print("=" * 92)
