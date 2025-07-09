# -*- coding: utf-8 -*- 
# NathalyCoronel-Reporte
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os
import sys
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configurar codificación UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Configuración inicial ---
REPORTS_DIR = "reportes"
os.makedirs(REPORTS_DIR, exist_ok=True)

# --- 1. Función para obtener datos desde la API ---
def fetch_libros_desde_api():
    try:
        response = requests.get('http://127.0.0.1:8000/api/books/')
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("⚠️ La API no devolvió datos.")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Validar columnas críticas
        required_columns = ['title', 'genres', 'ratings']
        for col in required_columns:
            if col not in df.columns:
                print(f"⚠️ Columna '{col}' no encontrada en los datos.")
                return pd.DataFrame()
        
        print("\n✅ Datos cargados correctamente. Primeras filas:")
        print(df[['title', 'genres']].head())
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión con la API: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error inesperado al obtener datos: {e}")
        return pd.DataFrame()

# --- 2. Función para obtener información de géneros ---
def obtener_info_generos(df):
    generos_info = {}
    try:
        for sublist in df['genres'].dropna():
            if isinstance(sublist, list):
                for g in sublist:
                    if isinstance(g, dict) and 'id' in g and 'name' in g:
                        if g['id'] not in generos_info:
                            generos_info[g['id']] = g['name']
        return generos_info
    except Exception as e:
        print(f"❌ Error al obtener géneros: {e}")
        return {}

# --- 3. Función de análisis mejorada ---
def analizar_libros(df, genero_usuario=None):
    resultados = {
        'genero_mas_valorado': None,
        'promedio_generos': {'ids': [], 'nombres': [], 'promedios': []},
        'top_3_libros': pd.DataFrame(),
        'top_3_genero': pd.DataFrame(),
        'genero_actual': None
    }

    try:
        # Calcular rating promedio por libro
        df['avg_rating'] = df['ratings'].apply(
            lambda x: round(sum(r['score'] for r in x) / len(x), 2) if x and len(x) > 0 else 0
        )
        
        generos_info = obtener_info_generos(df)
        if not generos_info:
            print("⚠️ No se encontraron géneros válidos para analizar.")
            return resultados

        # Análisis por género
        genero_ratings = []
        for genero_id, genero_nombre in generos_info.items():
            try:
                libros_genero = df[df['genres'].apply(
                    lambda x: genero_id in [g['id'] for g in x] if isinstance(x, list) else False
                )]
                
                if not libros_genero.empty:
                    avg = round(libros_genero['avg_rating'].mean(), 2)
                    genero_ratings.append((genero_id, genero_nombre, avg))
            except Exception as e:
                print(f"⚠️ Error analizando género {genero_id}: {e}")
                continue

        if genero_ratings:
            # Género más valorado
            genero_mas_valorado = max(genero_ratings, key=lambda x: x[2])
            resultados['genero_mas_valorado'] = genero_mas_valorado
            
            # Promedios por género
            resultados['promedio_generos'] = {
                'ids': [x[0] for x in genero_ratings],
                'nombres': [x[1] for x in genero_ratings],
                'promedios': [x[2] for x in genero_ratings]
            }

        # Top 3 libros global
        resultados['top_3_libros'] = df.sort_values('avg_rating', ascending=False).head(3)

        # Análisis por género específico
        if genero_usuario is not None:
            libros_genero = df[df['genres'].apply(
                lambda x: genero_usuario in [g['id'] for g in x] if isinstance(x, list) else False
            )]
            
            if not libros_genero.empty:
                resultados['top_3_genero'] = libros_genero.sort_values('avg_rating', ascending=False).head(3)
                resultados['genero_actual'] = {
                    'id': genero_usuario,
                    'nombre': generos_info.get(genero_usuario, 'Desconocido')
                }

    except Exception as e:
        print(f"❌ Error crítico en el análisis: {e}")
    
    return resultados

# --- 4. Generación de PDF  ---
def generar_pdf(resultados):
    if not resultados:
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(REPORTS_DIR, f'reporte_completo_{timestamp}.pdf')
    
    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Título principal
        elements.append(Paragraph("ANÁLISIS COMPLETO DE LIBROS", styles['Title']))
        elements.append(Spacer(1, 0.2 * inch))

        # 1. Género más valorado
        if resultados['genero_mas_valorado']:
            genero_id, genero_nombre, promedio = resultados['genero_mas_valorado']
            elements.append(Paragraph(
                f"Género más valorado: {genero_nombre} (ID: {genero_id}) con promedio de {promedio:.2f}⭐",
                styles['Heading2']
            ))
            elements.append(Spacer(1, 0.2 * inch))

        # 2. Promedios por género (gráfico)
        if resultados['promedio_generos']['ids']:
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=resultados['promedio_generos']['nombres'],
                y=resultados['promedio_generos']['promedios'],
                hue=resultados['promedio_generos']['nombres'],
                palette='viridis',
                legend=False,
                dodge=False
            )
            plt.title('Promedio de Valoraciones por Género', pad=20)
            plt.xlabel('Género')
            plt.ylabel('Rating Promedio')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            grafico_promedios = os.path.join(REPORTS_DIR, f'promedios_temp_{timestamp}.png')
            plt.savefig(grafico_promedios, dpi=300, bbox_inches='tight')
            plt.close()
            elements.append(Image(grafico_promedios, width=6 * inch, height=4 * inch))
            elements.append(Spacer(1, 0.3 * inch))

        # 3. Top 3 libros global
        if not resultados['top_3_libros'].empty:
            elements.append(Paragraph("Top 3 Libros Mejor Valorados (Global):", styles['Heading2']))
            data_global = [['Posición', 'Título', 'Rating', 'Géneros']]
            for i, (_, row) in enumerate(resultados['top_3_libros'].iterrows(), 1):
                generos = ", ".join([g['name'] for g in row['genres']]) if row['genres'] else "Sin géneros"
                data_global.append([str(i), row['title'], f"{row['avg_rating']:.2f}", generos])
            
            table_global = Table(data_global, colWidths=[0.5*inch, 3*inch, inch, 2*inch])
            table_global.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
            ]))
            elements.append(table_global)
            elements.append(Spacer(1, 0.3 * inch))

        # 4. Top 3 libros por género seleccionado
        if resultados.get('top_3_genero') is not None and not resultados['top_3_genero'].empty:
            elements.append(Paragraph(
                f"Top 3 Libros del Género: {resultados['genero_actual']['nombre']}",
                styles['Heading2']
            ))
            
            data_genero = [['Posición', 'Título', 'Rating']]
            for i, (_, row) in enumerate(resultados['top_3_genero'].iterrows(), 1):
                data_genero.append([str(i), row['title'], f"{row['avg_rating']:.2f}"])
            
            table_genero = Table(data_genero, colWidths=[0.5*inch, 4*inch, inch])
            table_genero.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ebf5fb'))
            ]))
            elements.append(table_genero)

        # Pie de página
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(
            f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Italic']
        ))

        doc.build(elements)
        
        # Limpiar archivos temporales
        if 'grafico_promedios' in locals():
            os.remove(grafico_promedios)
        
        print(f"\n✅ PDF generado: {pdf_path}")
        return True

    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        return False

# --- 5. Generación de Excel  ---
def generar_excel(resultados):
    try:
        if not resultados or resultados['top_3_libros'].empty:
            print("⚠️ No hay datos suficientes para generar Excel")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = os.path.join(REPORTS_DIR, f'reporte_{timestamp}.xlsx')

        # Crear un escritor Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Hoja 1: Top libros
            top_libros = resultados['top_3_libros'].copy()
            top_libros['genres'] = top_libros['genres'].apply(
                lambda x: ", ".join([g['name'] for g in x]) if isinstance(x, list) else "Sin géneros"
            )
            top_libros = top_libros[['title', 'avg_rating', 'genres']]
            top_libros.columns = ['Título', 'Rating Promedio', 'Géneros']
            top_libros.to_excel(writer, sheet_name='Top Libros', index=False)

            # Hoja 2: Análisis por género
            if resultados['promedio_generos']['ids']:
                df_generos = pd.DataFrame({
                    'Género': resultados['promedio_generos']['nombres'],
                    'ID': resultados['promedio_generos']['ids'],
                    'Rating Promedio': resultados['promedio_generos']['promedios']
                })
                df_generos.to_excel(writer, sheet_name='Géneros', index=False)

            # Hoja 3: Top por género específico
            if resultados.get('top_3_genero') is not None and not resultados['top_3_genero'].empty:
                top_genero = resultados['top_3_genero'].copy()
                top_genero['genres'] = top_genero['genres'].apply(
                    lambda x: ", ".join([g['name'] for g in x]) if isinstance(x, list) else "Sin géneros"
                )
                top_genero = top_genero[['title', 'avg_rating', 'genres']]
                top_genero.columns = ['Título', 'Rating Promedio', 'Géneros']
                top_genero.to_excel(writer, sheet_name=f"Top {resultados['genero_actual']['nombre']}", index=False)

        print(f"\n✅ Excel generado: {excel_path}")
        return True

    except PermissionError:
        print("❌ Error: No hay permisos para escribir en el directorio")
    except Exception as e:
        print(f"❌ Error al generar Excel: {e}")
    return False

# --- 6. Mostrar resultados en consola ---
def mostrar_resultados_consola(resultados):
    print("\n" + "="*50)
    print("📊 RESULTADOS DEL ANÁLISIS")
    print("="*50)
    
    if resultados['genero_mas_valorado']:
        genero_id, genero_nombre, promedio = resultados['genero_mas_valorado']
        print(f"\n⭐ Género más valorado: {genero_nombre} (ID: {genero_id})")
        print(f"   Promedio de rating: {promedio:.2f}")
    
    if resultados['promedio_generos']['ids']:
        print("\n📈 Promedio por géneros:")
        for id, nombre, prom in zip(
            resultados['promedio_generos']['ids'],
            resultados['promedio_generos']['nombres'],
            resultados['promedio_generos']['promedios']
        ):
            print(f"   {nombre} (ID: {id}): {prom:.2f}")
    
    if not resultados['top_3_libros'].empty:
        print("\n🏆 Top 3 Libros Mejor Valorados:")
        for i, (_, row) in enumerate(resultados['top_3_libros'].iterrows(), 1):
            generos = ", ".join([g['name'] for g in row['genres']]) if row['genres'] else "Sin géneros"
            print(f"   {i}. {row['title']} - {row['avg_rating']:.2f}⭐ ({generos})")
    
    if resultados.get('top_3_genero') is not None and not resultados['top_3_genero'].empty:
        print(f"\n🔥 Top 3 del Género {resultados['genero_actual']['nombre']}:")
        for i, (_, row) in enumerate(resultados['top_3_genero'].iterrows(), 1):
            print(f"   {i}. {row['title']} - {row['avg_rating']:.2f}⭐")

# --- 7. Menú interactivo  ---
def main():
    df = pd.DataFrame()
    
    while True:
        print("\n" + "="*50)
        print("📚 ANALIZADOR DE LIBROS - GENERADOR DE REPORTES")
        print("="*50)
        print("\n🔍 Menú Principal:")
        print("1. Cargar datos y generar reportes completos")
        print("2. Analizar género específico")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            if df.empty:
                df = fetch_libros_desde_api()
                if df.empty:
                    continue
            
            resultados = analizar_libros(df)
            mostrar_resultados_consola(resultados)
            
            # Generar ambos reportes
            print("\nGenerando reportes...")
            pdf_exitoso = generar_pdf(resultados)
            excel_exitoso = generar_excel(resultados)
            
            if pdf_exitoso and excel_exitoso:
                print("\n✅ Ambos reportes generados con éxito")
            elif pdf_exitoso:
                print("\n⚠️ Solo se generó el PDF (Error con Excel)")
            elif excel_exitoso:
                print("\n⚠️ Solo se generó el Excel (Error con PDF)")
            else:
                print("\n❌ No se pudo generar ningún reporte")
        
        elif opcion == '2':
            if df.empty:
                df = fetch_libros_desde_api()
                if df.empty:
                    continue
            
            generos_info = obtener_info_generos(df)
            if not generos_info:
                print("⚠️ No hay géneros disponibles para analizar.")
                continue
            
            print("\n📌 Géneros disponibles:")
            for id, nombre in sorted(generos_info.items()):
                print(f"{id}: {nombre}")
            
            try:
                genero_usuario = int(input("\nIngrese el ID del género a analizar: "))
                if genero_usuario not in generos_info:
                    print("⚠️ Error: El ID de género no existe.")
                    continue
                
                resultados = analizar_libros(df, genero_usuario)
                mostrar_resultados_consola(resultados)
                
                # Generar ambos reportes
                print("\nGenerando reportes...")
                pdf_exitoso = generar_pdf(resultados)
                excel_exitoso = generar_excel(resultados)
                
                if pdf_exitoso and excel_exitoso:
                    print("\n✅ Ambos reportes generados con éxito")
                elif pdf_exitoso:
                    print("\n⚠️ Solo se generó el PDF (Error con Excel)")
                elif excel_exitoso:
                    print("\n⚠️ Solo se generó el Excel (Error con PDF)")
                else:
                    print("\n❌ No se pudo generar ningún reporte")
            
            except ValueError:
                print("⚠️ Error: Debe ingresar un número válido.")
        
        elif opcion == '3':
            print("\n¡Gracias por usar el sistema! 👋")
            break
        
        else:
            print("⚠️ Opción no válida. Por favor intente de nuevo.")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import openpyxl
    except ImportError:
        print("\n❌ Error: Falta la librería 'openpyxl'. Instálela con:")
        print("pip install openpyxl")
        exit()

    main()