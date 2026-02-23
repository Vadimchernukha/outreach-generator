"""
csv_handler.py — чтение контактов и запись результатов
"""
import pandas as pd
import sys


def load_contacts(filepath: str, config: dict) -> tuple[pd.DataFrame, list[str]]:
    """
    Загружает CSV, определяет динамические колонки по boundary_column из конфига.
    Возвращает: (dataframe, список динамических колонок)
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    boundary = config.get("boundary_column", "")
    cols_lower = [c.lower() for c in df.columns]

    try:
        boundary_idx = cols_lower.index(boundary.lower())
        dynamic_cols = list(df.columns[boundary_idx + 1:])
    except ValueError:
        print(f"WARNING: boundary column '{boundary}' not found in CSV.")
        print(f"Available columns: {list(df.columns)}")
        dynamic_cols = []

    print(f"  Loaded {len(df)} contacts")
    print(f"  Dynamic columns ({len(dynamic_cols)}): {dynamic_cols}")
    return df, dynamic_cols


def get_field(row: pd.Series, internal_name: str, csv_mapping: dict) -> str:
    """
    Получает значение поля из строки CSV используя маппинг из конфига.
    Если точное имя не найдено — пробует регистронезависимый поиск.
    """
    csv_col = csv_mapping.get(internal_name, internal_name)

    # Прямое совпадение
    if csv_col in row.index:
        val = row[csv_col]
        if pd.notna(val) and str(val).strip() not in ("", "nan"):
            return str(val).strip()

    # Регистронезависимый поиск как запасной вариант
    for col in row.index:
        if col.lower() == csv_col.lower():
            val = row[col]
            if pd.notna(val) and str(val).strip() not in ("", "nan"):
                return str(val).strip()

    return ""


def build_dynamic_text(row: pd.Series, dynamic_cols: list[str]) -> str:
    """Форматирует динамические поля в читаемый текст для промпта."""
    lines = []
    skip_values = {"", "nan", "none", "false", "n/a", "na"}
    for col in dynamic_cols:
        val = row.get(col, "")
        if pd.notna(val) and str(val).strip().lower() not in skip_values:
            label = col.replace("_", " ").replace("-", " ").title()
            lines.append(f"- {label}: {val}")
    return "\n".join(lines) if lines else "No additional data available."


def save_results(rows: list[dict], filepath: str):
    """Сохраняет результаты в CSV."""
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(rows)} rows to: {filepath}")


def flatten_result(row: pd.Series, result: dict, csv_mapping: dict) -> list[dict]:
    """Разворачивает результат одного контакта в строки CSV (по одной на сообщение)."""
    base = {
        "person_name":     get_field(row, "person_name", csv_mapping),
        "company_name":    get_field(row, "company_name", csv_mapping),
        "title":           get_field(row, "title", csv_mapping),
        "industry":        get_field(row, "industry", csv_mapping),
        "company_country": get_field(row, "company_country", csv_mapping),
        "website":         get_field(row, "website", csv_mapping),
        "company_size":    get_field(row, "company_size", csv_mapping),
        "strategy":        result.get("strategy_rationale", ""),
        "error":           result.get("error", ""),
    }

    if not result.get("messages"):
        return [base]

    output = []
    for msg in result["messages"]:
        r = base.copy()
        r.update({
            "message_step":     msg.get("step", ""),
            "send_after":       msg.get("send_after", ""),
            "angle":            msg.get("angle", ""),
            "original_message": msg.get("original_text", ""),
            "final_message":    msg.get("humanized_text", ""),
        })
        output.append(r)
    return output
