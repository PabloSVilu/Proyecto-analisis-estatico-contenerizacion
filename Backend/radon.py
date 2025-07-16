import subprocess
import sys
import os

def run_radon(target_path):
    if not os.path.exists(target_path):
        print(f"❌ Error: El archivo o carpeta '{target_path}' no existe.")
        return

    print(f"\n🔍 Ejecutando Radon sobre: {target_path}...\n")

    try:
        # Ejecutar Radon
        result = subprocess.run(
            ['radon', 'cc', target_path, '-a'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout
        print(output)

        # Guardar resultado en archivo
        report_file = "radon-report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"\n✅ Reporte guardado en '{report_file}'.")

        # Mostrar resumen general
        summary_line = next((line for line in output.splitlines() if line.startswith('Average complexity')), None)
        if summary_line:
            print(f"\n📊 {summary_line}")
        else:
            print("\n⚠️ No se encontró un resumen de complejidad promedio.")

    except Exception as e:
        print(f"❌ Error ejecutando Radon: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python radon.py <archivo_o_carpeta>")
    else:
        run_radon(sys.argv[1])
