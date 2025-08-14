#!/usr/bin/env python3
import os
import sys
import argparse
from decimal import Decimal

from sqlalchemy import create_engine, text

# Deterministic IDs for seed data
USER_1_ID = "11111111-1111-1111-1111-111111111111"
USER_2_ID = "22222222-2222-2222-2222-222222222222"

EVT_1_ID = "f1111111-1111-1111-1111-111111111111"
EVT_1_EVENT_ID = "e1111111-1111-1111-1111-111111111111"
EVT_2_ID = "f2222222-2222-2222-2222-222222222222"
EVT_2_EVENT_ID = "e2222222-2222-2222-2222-222222222222"
EVT_3_ID = "f3333333-3333-3333-3333-333333333333"
EVT_3_EVENT_ID = "e3333333-3333-3333-3333-333333333333"

RA_1_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"  # approved
RA_2_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"  # declined

OFFER_1_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"  # proposed

ACC_1_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"  # active credit account for USER_1


def should_seed(cli_yes: bool) -> bool:
    if cli_yes:
        return True
    return os.getenv("SEED_DEV_DATA", "").lower() in ("1", "true", "yes", "on")


def seed(db_url: str) -> None:
    engine = create_engine(db_url)

    with engine.begin() as conn:
        # Users (password column is required by current schema)
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_1_ID, "full_name": "Alice Merchant", "email": "alice@example.com", "password": "password-hash"},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_2_ID, "full_name": "Bob Retailer", "email": "bob@example.com", "password": "password-hash"},
        )

        # Emotional events for USER_1
        conn.execute(
            text(
                """
                INSERT INTO emotional_events (
                    id, user_id, event_id,
                    emotion_primary, emotion_confidence,
                    arousal, valence,
                    captured_at
                )
                VALUES (
                    :id, :user_id, :event_id,
                    :emotion_primary, :emotion_confidence,
                    :arousal, :valence,
                    NOW() - INTERVAL '1 day'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_1_ID,
                "user_id": USER_1_ID,
                "event_id": EVT_1_EVENT_ID,
                "emotion_primary": "joy",
                "emotion_confidence": 0.92,
                "arousal": 0.65,
                "valence": 0.8,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO emotional_events (
                    id, user_id, event_id,
                    emotion_primary, emotion_confidence,
                    arousal, valence,
                    captured_at
                )
                VALUES (
                    :id, :user_id, :event_id,
                    :emotion_primary, :emotion_confidence,
                    :arousal, :valence,
                    NOW() - INTERVAL '2 hours'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_2_ID,
                "user_id": USER_1_ID,
                "event_id": EVT_2_EVENT_ID,
                "emotion_primary": "calm",
                "emotion_confidence": 0.86,
                "arousal": 0.3,
                "valence": 0.6,
            },
        )

        # Emotional event for USER_2
        conn.execute(
            text(
                """
                INSERT INTO emotional_events (
                    id, user_id, event_id,
                    emotion_primary, emotion_confidence,
                    arousal, valence,
                    captured_at
                )
                VALUES (
                    :id, :user_id, :event_id,
                    :emotion_primary, :emotion_confidence,
                    :arousal, :valence,
                    NOW() - INTERVAL '3 hours'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_3_ID,
                "user_id": USER_2_ID,
                "event_id": EVT_3_EVENT_ID,
                "emotion_primary": "anxiety",
                "emotion_confidence": 0.74,
                "arousal": 0.7,
                "valence": -0.2,
            },
        )

        # Risk assessments
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, decision)
                VALUES (:id, :user_id, :risk_score, :decision)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_1_ID, "user_id": USER_1_ID, "risk_score": Decimal("0.23"), "decision": "approved"},
        )
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, decision)
                VALUES (:id, :user_id, :risk_score, :decision)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_2_ID, "user_id": USER_2_ID, "risk_score": Decimal("0.81"), "decision": "declined"},
        )

        # Credit offer for USER_1, linked to approved risk assessment
        conn.execute(
            text(
                """
                INSERT INTO credit_offers (
                    id, user_id, risk_assessment_id,
                    credit_type, credit_limit, apr,
                    status, expires_at
                )
                VALUES (
                    :id, :user_id, :risk_assessment_id,
                    :credit_type, :credit_limit, :apr,
                    'proposed', NOW() + INTERVAL '14 days'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": OFFER_1_ID,
                "user_id": USER_1_ID,
                "risk_assessment_id": RA_1_ID,
                "credit_type": "short_term",
                "credit_limit": Decimal("5000.00"),
                "apr": Decimal("29.99"),
            },
        )

        # Active credit account for USER_1
        conn.execute(
            text(
                """
                INSERT INTO credit_accounts (
                    id, user_id, active_limit, apr, credit_type,
                    current_balance, available_credit
                )
                VALUES (
                    :id, :user_id, :active_limit, :apr, :credit_type,
                    :current_balance, :available_credit
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": ACC_1_ID,
                "user_id": USER_1_ID,
                "active_limit": Decimal("3000.00"),
                "apr": Decimal("24.99"),
                "credit_type": "revolving",
                "current_balance": Decimal("750.00"),
                "available_credit": Decimal("2250.00"),
            },
        )

    print("Seed completed.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed deterministic dev data")
    parser.add_argument("--yes", action="store_true", help="Run seeding without interactive prompt")
    args = parser.parse_args()

    db_url = os.getenv("DB_URL", "")
    if not db_url:
        print("ERROR: DB_URL env var is required")
        return 2

    if not should_seed(args.yes):
        print("Refusing to seed: pass --yes or set SEED_DEV_DATA=1")
        return 0

    try:
        seed(db_url)
        return 0
    except Exception as exc:
        print(f"ERROR: seeding failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
