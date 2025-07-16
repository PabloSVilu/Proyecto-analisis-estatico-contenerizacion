import subprocess
import sys
import os
import re

def run_pylint(target_path):
    if not os.path.exists(target_path):
        print(f" Error: El archivo o carpeta '{target_path}' no existe.")
        return

    print(f"\n Ejecutando pylint sobre: {target_path}...\n")

    try:
        # Ejecutar pylint
        result = subprocess.run(
            ['pylint', target_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout
        print(output)

        # Guardar en archivo
        report_file = "pylint-report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"\n Reporte guardado en '{report_file}'.")

        # Analizar errores por tipo
        error_summary = {
            'convention': 0,
            'refactor': 0,
            'warning': 0,
            'error': 0,
            'fatal': 0
        }

        for line in output.splitlines():
            match = re.search(r": ([CRWEF])\d{4}", line)
            if match:
                code_type = match.group(1)
                if code_type == "C":
                    error_summary["convention"] += 1
                elif code_type == "R":
                    error_summary["refactor"] += 1
                elif code_type == "W":
                    error_summary["warning"] += 1
                elif code_type == "E":
                    error_summary["error"] += 1
                elif code_type == "F":
                    error_summary["fatal"] += 1

        print("\n Resumen de errores:")
        for tipo, cantidad in error_summary.items():
            print(f"  - {tipo.capitalize()}: {cantidad}")

        if result.returncode != 0:
            print("\n ¡Pylint encontró problemas en el código!")
        else:
            print("\n ¡Código limpio según Pylint!")

    except Exception as e:
        print(f" Error ejecutando pylint: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python run_pylint.py <archivo_o_carpeta>")
    else:
        run_pylint(sys.argv[1])
