def bool_calculator(a, b, operation):
    """
    Выполняет логические операции над булевыми значениями.
    """
    if operation == 'and':
        return a and b
    elif operation == 'or':
        return a or b
    elif operation == 'not':
        return not a
    else:
        return None


def truth_table_generator():
    """
    Генерирует и выводит таблицу истинности для выражения F = (A and not B) or (not A and B)
    """
    print(" A | B | F")
    print("-----------")
    
    for a in [False, True]:
        for b in [False, True]:
            f = (a and not b) or (not a and b)
            a_display = 1 if a else 0
            b_display = 1 if b else 0
            f_display = 1 if f else 0
            print(f" {a_display} | {b_display} | {f_display}")


def print_circuit():
    """
    Визуализирует логическую схему для выражения F = (A and not B) or (not A and B)
    """
    circuit = """
     A ---[NOT]--\\
                  > [OR] --- F
     B ---[NOT]--/
    """
    print(circuit)


def main():
    print("=== ПРАКТИЧЕСКОЕ ЗАДАНИЕ: ВАЛИДАТОР ЛОГИЧЕСКИХ ВЫРАЖЕНИЙ ===\n")
    
    print("1. Базовый калькулятор:")
    print(f"True AND False = {bool_calculator(True, False, 'and')}")
    print(f"True OR False = {bool_calculator(True, False, 'or')}")
    print(f"NOT True = {bool_calculator(True, None, 'not')}")
    print(f"Unknown operation = {bool_calculator(True, False, 'xor')}")
    print()
    
    print("2. Таблица истинности для F = (A and not B) or (not A and B):")
    truth_table_generator()
    print()
    
    print("3. Визуализация логической схемы:")
    print_circuit()

main()