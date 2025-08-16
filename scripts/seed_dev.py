#!/usr/bin/env python3
import os
import sys
import argparse
from decimal import Decimal

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Create password hashing context (same as in security.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Deterministic IDs for seed data
USER_1_ID = "11111111-1111-1111-1111-111111111111"
USER_2_ID = "22222222-2222-2222-2222-222222222222"
USER_3_ID = "33333333-3333-3333-3333-333333333333"  # no events of any kind
USER_4_ID = "44444444-4444-4444-4444-444444444444"  # transactions only
USER_5_ID = "55555555-5555-5555-5555-555555555555"  # emotions only
USER_6_ID = "66666666-6666-6666-6666-666666666666"  # mixed + accepted offer/account
USER_7_ID = "77777777-7777-7777-7777-777777777777"  # expired assessment + expired offer
USER_8_ID = "88888888-8888-8888-8888-888888888888"  # assessment only, no offer

EVT_1_ID = "f1111111-1111-1111-1111-111111111111"
EVT_1_EVENT_ID = "e1111111-1111-1111-1111-111111111111"
EVT_2_ID = "f2222222-2222-2222-2222-222222222222"
EVT_2_EVENT_ID = "e2222222-2222-2222-2222-222222222222"
EVT_3_ID = "f3333333-3333-3333-3333-333333333333"
EVT_3_EVENT_ID = "e3333333-3333-3333-3333-333333333333"

# Additional emotional events
EVT_4_ID = "f4444444-4444-4444-4444-444444444444"
EVT_4_EVENT_ID = "e4444444-4444-4444-4444-444444444444"  # user5
EVT_5_ID = "f5555555-5555-5555-5555-555555555555"
EVT_5_EVENT_ID = "e5555555-5555-5555-5555-555555555555"  # user5
EVT_6_ID = "f6666666-6666-6666-6666-666666666666"
EVT_6_EVENT_ID = "e6666666-6666-6666-6666-666666666666"  # user6
EVT_7_ID = "f7777777-7777-7777-7777-777777777777"
EVT_7_EVENT_ID = "e7777777-7777-7777-7777-777777777777"  # user6

# Risk assessments
RA_1_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"  # for USER_1
RA_2_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"  # for USER_2
RA_3_ID = "cccccccc-cccc-cccc-cccc-ccccccccccca"  # for USER_6 accepted offer
RA_4_ID = "dddddddd-dddd-dddd-dddd-ddddddddddda"  # for USER_7 expired
RA_5_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeea"  # for USER_8 assessment only

# Credit offers
OFFER_1_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"  # proposed for USER_1
OFFER_2_ID = "cccccccc-cccc-cccc-cccc-cccccccccccb"  # accepted for USER_6
OFFER_3_ID = "cccccccc-cccc-cccc-cccc-cccccccccccd"  # expired for USER_7

# Credit accounts
ACC_1_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"  # active credit account for USER_1
ACC_2_ID = "dddddddd-dddd-dddd-dddd-ddddddddddde"  # active credit account for USER_6

# Deterministic transaction IDs
TX4_1_ID = "44440000-0000-0000-0000-000000000001"
TX4_2_ID = "44440000-0000-0000-0000-000000000002"
TX4_3_ID = "44440000-0000-0000-0000-000000000003"
TX6_1_ID = "66660000-0000-0000-0000-000000000001"
TX6_2_ID = "66660000-0000-0000-0000-000000000002"

# API client
CLIENT_1_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"


def should_seed(cli_yes: bool) -> bool:
    if cli_yes:
        return True
    return os.getenv("SEED_DEV_DATA", "").lower() in ("1", "true", "yes", "on")


def seed(db_url: str) -> None:
    engine = create_engine(db_url)

    with engine.begin() as conn:
        # API Client
        conn.execute(
            text(
                """
                INSERT INTO clients (id, client_id, client_secret, name)
                VALUES (:id, :client_id, :client_secret, :name)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": CLIENT_1_ID,
                "client_id": "ecs-ingest",
                "client_secret": hash_password("oz`]:u`RYz#ZN];"),
                "name": "ECS Ingestion Service",
            },
        )

        # Users (password column is required by current schema)
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_1_ID, "full_name": "Alice Merchant", "email": "alice@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_2_ID, "full_name": "Bob Retailer", "email": "bob@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_3_ID, "full_name": "Charlie NoEvents", "email": "charlie@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_4_ID, "full_name": "Diana TxOnly", "email": "diana@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_5_ID, "full_name": "Eve EmotionsOnly", "email": "eve@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_6_ID, "full_name": "Frank Mixed", "email": "frank@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_7_ID, "full_name": "Grace Expired", "email": "grace@example.com", "password": hash_password("password123")},
        )
        conn.execute(
            text(
                """
                INSERT INTO users (id, full_name, email, password)
                VALUES (:id, :full_name, :email, :password)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": USER_8_ID, "full_name": "Heidi AssessOnly", "email": "heidi@example.com", "password": hash_password("password123")},
        )

        # Emotional events for USER_1 and USER_2 (existing)
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

        # Emotional events for USER_5 (emotions only)
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
                    NOW() - INTERVAL '5 hours'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_4_ID,
                "user_id": USER_5_ID,
                "event_id": EVT_4_EVENT_ID,
                "emotion_primary": "surprise",
                "emotion_confidence": 0.8,
                "arousal": 0.75,
                "valence": 0.1,
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
                    NOW() - INTERVAL '30 minutes'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_5_ID,
                "user_id": USER_5_ID,
                "event_id": EVT_5_EVENT_ID,
                "emotion_primary": "joy",
                "emotion_confidence": 0.9,
                "arousal": 0.55,
                "valence": 0.85,
            },
        )

        # Emotional events for USER_6 (mixed)
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
                    NOW() - INTERVAL '12 hours'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_6_ID,
                "user_id": USER_6_ID,
                "event_id": EVT_6_EVENT_ID,
                "emotion_primary": "calm",
                "emotion_confidence": 0.82,
                "arousal": 0.25,
                "valence": 0.5,
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
                    NOW() - INTERVAL '10 minutes'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": EVT_7_ID,
                "user_id": USER_6_ID,
                "event_id": EVT_7_EVENT_ID,
                "emotion_primary": "joy",
                "emotion_confidence": 0.88,
                "arousal": 0.6,
                "valence": 0.9,
            },
        )

        # Transactions for USER_4 (transactions only)
        tx4 = [
            (TX4_1_ID, 1440, Decimal("1200.00")),
            (TX4_2_ID, 720, Decimal("-250.50")),
            (TX4_3_ID, 60, Decimal("300.00")),
        ]
        for tx_id, minutes_ago, amount in tx4:
            conn.execute(
                text(
                    """
                    INSERT INTO transactions (id, user_id, amount, currency, occurred_at)
                    VALUES (:id, :user_id, :amount, :currency, NOW() - make_interval(mins => :mins))
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": tx_id,
                    "user_id": USER_4_ID,
                    "amount": amount,
                    "currency": "BRL",
                    "mins": minutes_ago,
                },
            )

        # Transactions for USER_6 (mixed)
        tx6 = [
            (TX6_1_ID, 2880, Decimal("500.00")),
            (TX6_2_ID, 5, Decimal("-120.75")),
        ]
        for tx_id, minutes_ago, amount in tx6:
            conn.execute(
                text(
                    """
                    INSERT INTO transactions (id, user_id, amount, currency, occurred_at)
                    VALUES (:id, :user_id, :amount, :currency, NOW() - make_interval(mins => :mins))
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": tx_id,
                    "user_id": USER_6_ID,
                    "amount": amount,
                    "currency": "BRL",
                    "mins": minutes_ago,
                },
            )

        # Risk assessments (updated schema: no decision, with expires_at)
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, expires_at)
                VALUES (:id, :user_id, :risk_score, NOW() + INTERVAL '30 days')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_1_ID, "user_id": USER_1_ID, "risk_score": Decimal("0.23")},
        )
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, expires_at)
                VALUES (:id, :user_id, :risk_score, NOW() + INTERVAL '10 days')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_2_ID, "user_id": USER_2_ID, "risk_score": Decimal("0.81")},
        )
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, expires_at)
                VALUES (:id, :user_id, :risk_score, NOW() + INTERVAL '60 days')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_3_ID, "user_id": USER_6_ID, "risk_score": Decimal("0.45")},
        )
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, expires_at)
                VALUES (:id, :user_id, :risk_score, NOW() - INTERVAL '7 days')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_4_ID, "user_id": USER_7_ID, "risk_score": Decimal("0.65")},
        )
        conn.execute(
            text(
                """
                INSERT INTO risk_assessments (id, user_id, risk_score, expires_at)
                VALUES (:id, :user_id, :risk_score, NOW() + INTERVAL '90 days')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": RA_5_ID, "user_id": USER_8_ID, "risk_score": Decimal("0.30")},
        )

        # Credit offers
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
                    'Offered', NOW() + INTERVAL '14 days'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": OFFER_1_ID,
                "user_id": USER_1_ID,
                "risk_assessment_id": RA_1_ID,
                "credit_type": "Short term",
                "credit_limit": Decimal("5000.00"),
                "apr": Decimal("29.99"),
            },
        )

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
                    'Accepted', NOW() + INTERVAL '28 days'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": OFFER_2_ID,
                "user_id": USER_6_ID,
                "risk_assessment_id": RA_3_ID,
                "credit_type": "Long term",
                "credit_limit": Decimal("10000.00"),
                "apr": Decimal("19.99"),
            },
        )

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
                    'Offered', NOW() - INTERVAL '1 day'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": OFFER_3_ID,
                "user_id": USER_7_ID,
                "risk_assessment_id": RA_4_ID,
                "credit_type": "Short term",
                "credit_limit": Decimal("1500.00"),
                "apr": Decimal("34.99"),
            },
        )

        # Active credit accounts
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
                "credit_type": "Long term",
                "current_balance": Decimal("750.00"),
                "available_credit": Decimal("2250.00"),
            },
        )
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
                "id": ACC_2_ID,
                "user_id": USER_6_ID,
                "active_limit": Decimal("10000.00"),
                "apr": Decimal("19.99"),
                "credit_type": "Short term",
                "current_balance": Decimal("1200.00"),
                "available_credit": Decimal("8800.00"),
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
