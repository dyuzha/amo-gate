import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Запуск сервиса с поддержкой мокинга lead_id"
    )
    parser.add_argument(
        "--mocked-lead-id",
        action="store_true",  # Флаг (True/False)
        default=False,        # По умолчанию отключено
        help="Включить режим мокинга lead_id (default: False)"
    )
    return parser.parse_args()
