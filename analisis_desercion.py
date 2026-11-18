from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    # TODO 1: imprimir shape, info(), describe() y value_counts() de las columnas indicadas.
    print("=" * 70)
    print("PASO 1: PRIMERA MIRADA AL DATASET")
    print("=" * 70)
    print("\nForma (filas, columnas):", df.shape)
    print("\nTipos y no nulos por columna:")
    df.info()
    print("\nNulos por columna:")
    print(df.isnull().sum())
    print("\nEstadísticas de las columnas numéricas:")
    print(df.describe().T)
    for col in ["programa", "jornada", "genero", "estado"]:
        print(f"\nvalue_counts de {col}:")
        print(df[col].value_counts(dropna=False))
    # Respuesta a la pregunta: asistencia_pct y horas_trabajo_semana aparecen como texto
    # (str) aunque deberían ser números, porque traen el símbolo '%' o el guion '-'.
    texto_numerico = [c for c in ["asistencia_pct", "horas_trabajo_semana"] if not pd.api.types.is_numeric_dtype(df[c])]
    print("\nColumnas que deberían ser numéricas pero llegan como texto:", texto_numerico)


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
     # TODO 2: imprimir cada uno de los conteos de problemas.
    print("\n" + "=" * 70)
    print("PASO 2: AUDITORÍA DE CALIDAD (sin corregir)")
    print("=" * 70)

    print("\n[Nulos reales por columna]")
    nulos = df.isnull().sum()
    print(nulos[nulos > 0])

    print("\n[Faltantes disfrazados]")
    print("Guiones '-' en asistencia_pct:      ", (df["asistencia_pct"] == "-").sum())
    print("Guiones '-' en horas_trabajo_semana:", (df["horas_trabajo_semana"] == "-").sum())
    print("Valores 999 en distancia_km:        ", (df["distancia_km"] == 999).sum())

    print("\n[Formato inconsistente]")
    print("Celdas de asistencia_pct con el signo %:", df["asistencia_pct"].str.contains("%", regex=False).sum())
    fechas = df["fecha_matricula"].astype(str)
    print("Fechas en formato DD/MM/AAAA:", fechas.str.contains("/", regex=False).sum())
    print("Fechas en formato AAAA-MM-DD:", fechas.str.match(r"^\d{4}-\d{2}-\d{2}$").sum())

    print("\n[Valores imposibles]")
    print("Edad fuera de 15 a 60:       ", ((df["edad"] < 15) | (df["edad"] > 60)).sum())
    print("promedio_acumulado > 5:      ", (df["promedio_acumulado"] > 5).sum())
    horas = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    print("horas_trabajo_semana > 100:  ", (horas > 100).sum())

    print("\n[Duplicados]")
    print("Filas duplicadas (todas las columnas iguales):", df.duplicated().sum())
    print("id_estudiante repetidos:                      ", df["id_estudiante"].duplicated().sum())

    print("\n[Errores tipográficos: valores distintos por columna categórica]")
    for col in VALIDOS:
        print(f"  {col}: {df[col].nunique()} valores distintos (válidos: {len(VALIDOS[col])})")

    print("\n[Nulos esperados]")
    print("motivo_retiro es nulo en:", df.loc[df["motivo_retiro"].isnull(), "estado"].value_counts().to_dict())
    # Respuesta: el problema que más afecta el análisis es el de promedio_acumulado, porque
    # los valores imposibles (45, 62, 78) inflan el promedio y los nulos reducen la muestra;
    # además, los duplicados cuentan dos veces a un mismo estudiante y distorsionan las tasas.


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
     # TODO 3: convertir asistencia_pct, horas_trabajo_semana y distancia_km a número.
    # asistencia_pct: quitar '%' y convertir los guiones en nulos reales.
    n_pct = df["asistencia_pct"].str.contains("%", regex=False).sum()
    n_guion = (df["asistencia_pct"] == "-").sum()
    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"].replace("-", np.nan), errors="coerce")
    registrar("convertir_numericos", "asistencia_pct", "quitar símbolo % y convertir a número", n_pct,
              "El % es solo formato; sin quitarlo la columna es texto y no se puede promediar.")
    registrar("convertir_numericos", "asistencia_pct", "reemplazar '-' por nulo real", n_guion,
              "El guion es un faltante disfrazado: no se conoce la asistencia y no se inventa.")

    # horas_trabajo_semana: los guiones pasan a nulo (se tratan en el paso 8 según 'trabaja').
    n_guion_h = (df["horas_trabajo_semana"] == "-").sum()
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")
    registrar("convertir_numericos", "horas_trabajo_semana", "reemplazar '-' por nulo y convertir a número", n_guion_h,
              "El guion es un faltante disfrazado; se vuelve nulo real para tratarlo con una regla en el paso 8.")

    # distancia_km: 999 es un código de 'sin dato', no una distancia.
    n_999 = (df["distancia_km"] == 999).sum()
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)
    registrar("convertir_numericos", "distancia_km", "reemplazar 999 por nulo", n_999,
              "999 km es un código de 'sin dato'; dejarlo inflaría el promedio de distancia (la media pasa de ~17 km a ~32 km).")
    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    # TODO 4: unificar las escrituras de programa, jornada, genero y ciudad_procedencia.
    antes = {col: df[col].nunique() for col in VALIDOS}
    # Variantes (ya en minúsculas y sin espacios) -> forma correcta.
    variantes = {
        "programa": {"ingenieria de sistemas": "Ingeniería de Sistemas", "psicologia": "Psicología"},
        "jornada": {},
        "genero": {"m": "Masculino", "f": "Femenino"},
        "ciudad_procedencia": {"bogota": "Bogotá", "medellin": "Medellín"},
    }
    for col, validos in VALIDOS.items():
        original = df[col].copy()
        df[col] = df[col].str.strip().str.lower()
        # Cada valor válido en minúsculas apunta a su forma correcta.
        mapa = {v.lower(): v for v in validos}
        mapa.update(variantes[col])
        df[col] = df[col].replace(mapa)
        cambiadas = (original != df[col]) & original.notnull()
        fuera = sorted(set(df[col].dropna()) - set(validos))
        registrar("unificar_categorias", col, "strip + lower + diccionario de variantes", cambiadas.sum(),
                  f"Mismo valor escrito distinto (mayúsculas, tildes, abreviaturas). "
                  f"Valores distintos: {antes[col]} -> {df[col].nunique()}.")
        print(f"  {col}: {antes[col]} -> {df[col].nunique()} valores; fuera de VALIDOS: {fuera}")
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    # TODO 5: convertir fecha_matricula a fecha con los dos formatos.
    texto = df["fecha_matricula"].astype(str)
    n_dmy = texto.str.contains("/", regex=False).sum()
    iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
    dmy = pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")
    df["fecha_matricula"] = iso.fillna(dmy)
    sin_fecha = df["fecha_matricula"].isnull().sum()
    registrar("convertir_fechas", "fecha_matricula", "convertir a fecha (AAAA-MM-DD y DD/MM/AAAA)", n_dmy,
              f"Fechas en dos formatos; se probó cada uno con formato explícito para no confundir día y mes. "
              f"Fechas sin convertir: {sin_fecha}.")
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    # TODO 6: eliminar duplicados, registrar la decisión y devolver el dataframe.
    # Dos estudiantes distintos tendrían id_estudiante distinto, así que una fila idéntica
    # en las 23 columnas (incluido el id) es el mismo registro cargado dos veces.
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    registrar("duplicados", "todas", "eliminar filas duplicadas (se conserva la primera)", n_dup,
              "Fila idéntica en todas las columnas, incluido id_estudiante: es el mismo estudiante contado dos veces.")
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # TODO 7: tratar los nulos de promedio_acumulado, ciudad_procedencia y tipo_colegio.
    # promedio_acumulado: una nota no se puede inventar ni imputar con el promedio.
    n_prom = df["promedio_acumulado"].isnull().sum()
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("faltantes", "promedio_acumulado", "eliminar filas con nulo", n_prom,
              "Una nota no se puede inventar; imputar el promedio encogería la variabilidad y sesgaría las comparaciones.")

    # ciudad_procedencia y tipo_colegio: se conservan las filas y se marca 'Sin dato'.
    for col in ["ciudad_procedencia", "tipo_colegio"]:
        n = df[col].isnull().sum()
        df[col] = df[col].fillna("Sin dato")
        registrar("faltantes", col, "reemplazar nulo por 'Sin dato'", n,
                  "Eliminar la fila perdería un estudiante con el resto de datos válidos; 'Sin dato' conserva la fila y se ve como grupo aparte.")

    # motivo_retiro: no se toca. Es nulo en todos los activos y graduados porque no aplica.
    n_mot = df["motivo_retiro"].isnull().sum()
    registrar("faltantes", "motivo_retiro", "dejar nulo (sin cambios)", n_mot,
              "Nulo esperado: solo aplica a desertores, así que no es un error y no se imputa.")
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # TODO 8: tratar edad, promedio_acumulado y horas_trabajo_semana, con sus justificaciones.
    # promedio_acumulado: la escala es 0 a 5; 45, 62 y 78 no existen. No se reescalan (sería inventar
    # la nota): se marcan como nulos y, como en el paso 7, se eliminan esas filas.
    imposibles = df["promedio_acumulado"] > 5
    n_prom = imposibles.sum()
    df.loc[imposibles, "promedio_acumulado"] = np.nan
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)
    registrar("imposibles", "promedio_acumulado", "valores > 5 -> nulo -> eliminar filas", n_prom,
              "Escala de 0 a 5: valores como 45, 62 o 78 son errores de registro; reescalarlos sería adivinar la nota.")

    # edad: fuera de 15 a 60 es un error (12 y 150 años); se reemplaza por la mediana de las edades válidas.
    fuera = (df["edad"] < 15) | (df["edad"] > 60)
    n_edad = fuera.sum()
    mediana_edad = df.loc[~fuera, "edad"].median()
    df.loc[fuera, "edad"] = mediana_edad
    registrar("imposibles", "edad", f"fuera de 15-60 -> mediana ({mediana_edad:.0f})", n_edad,
              "Edades de 12 o 150 años no son plausibles para estudiantes; la mediana no se ve afectada por extremos y la fila conserva sus demás datos.")

    # horas_trabajo_semana: quien no trabaja tiene 0 horas; valores > 100 son imposibles.
    sin_trabajo = (df["trabaja"] == "no") & df["horas_trabajo_semana"].isnull()
    n_cero = sin_trabajo.sum()
    df.loc[sin_trabajo, "horas_trabajo_semana"] = 0
    registrar("imposibles", "horas_trabajo_semana", "trabaja='no' y horas nulas -> 0", n_cero,
              "Si el estudiante no trabaja, sus horas de trabajo son 0; no es un faltante sino un cero real.")

    extremos = df["horas_trabajo_semana"] > 100
    n_ext = extremos.sum()
    mediana_horas = df.loc[(df["trabaja"] == "sí") & ~extremos, "horas_trabajo_semana"].median()
    df.loc[extremos, "horas_trabajo_semana"] = np.nan
    df["horas_trabajo_semana"] = df["horas_trabajo_semana"].fillna(mediana_horas)
    registrar("imposibles", "horas_trabajo_semana", f"> 100 -> nulo -> mediana de quienes trabajan ({mediana_horas:.0f})", n_ext,
              "Más de 100 horas semanales (200) es casi inviable junto a estudiar; se usa la mediana de quienes sí trabajan.")

    # Nulos que quedan sin tratar a propósito (se registran para dejar constancia).
    for col, motivo in [("asistencia_pct", "No se inventa la asistencia; los cuartiles y promedios ignoran los nulos."),
                        ("distancia_km", "No se inventa la distancia; no se usa en las cinco preguntas.")]:
        registrar("imposibles", col, "dejar nulos sin imputar", df[col].isnull().sum(), motivo)
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    # TODO 9: crear las columnas desertor y cuartil_asistencia.
    df["desertor"] = df["estado"].eq("desertor")
    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    registrar("variables", "desertor", "crear columna booleana (estado == 'desertor')", df["desertor"].sum(),
              "Convierte el resultado en True/False; su promedio es directamente la tasa de deserción.")
    registrar("variables", "cuartil_asistencia", "crear cuartiles de asistencia con pd.qcut", df["cuartil_asistencia"].notnull().sum(),
              "Cuatro grupos del mismo tamaño dan tasas comparables y estables; con valores exactos cada grupo sería diminuto.")
    print(f"Desertores: {df['desertor'].sum()} de {len(df)} estudiantes ({df['desertor'].mean():.1%}).")
    # Respuesta: los cuartiles permiten ver el patrón en grupos grandes del mismo tamaño en vez de
    # cientos de valores de asistencia con pocos estudiantes cada uno.
    return df


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    # TODO 10: dibujar, guardar en GRAFICOS / "mapa_faltantes.png" y mostrar.
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False)
    plt.title("Mapa de faltantes del dataset original (franja clara = celda vacía)")
    plt.xlabel("Columna")
    plt.ylabel("Fila")
    plt.yticks([])
    plt.savefig(GRAFICOS / "mapa_faltantes.png", bbox_inches="tight")
    plt.show()
    plt.close()


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    # TODO 11: dibujar los cuatro boxplots, guardar en GRAFICOS / "distribuciones_antes_despues.png" y mostrar.
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8))
    sns.boxplot(x=antes["promedio_acumulado"], ax=ejes[0, 0])
    ejes[0, 0].set_title("promedio_acumulado (antes)")
    sns.boxplot(x=despues["promedio_acumulado"], ax=ejes[0, 1])
    ejes[0, 1].set_title("promedio_acumulado (después)")
    sns.boxplot(x=antes["edad"], ax=ejes[1, 0])
    ejes[1, 0].set_title("edad (antes)")
    sns.boxplot(x=despues["edad"], ax=ejes[1, 1])
    ejes[1, 1].set_title("edad (después)")
    fig.suptitle("Distribuciones antes y después de limpiar")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "distribuciones_antes_despues.png", bbox_inches="tight")
    plt.show()
    plt.close()


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    # TODO 12: dibujar la tasa por programa, guardar en GRAFICOS / "tasa_desercion_por_programa.png" y mostrar.
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("programa")["desertor"].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por programa")
    plt.ylabel("Tasa de deserción")
    plt.xlabel("Programa")
    plt.xticks(rotation=45, ha="right")
    plt.savefig(GRAFICOS / "tasa_desercion_por_programa.png", bbox_inches="tight")
    plt.show()
    plt.close()


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    # TODO 13: dibujar la tasa por cuartil, guardar en GRAFICOS / "tasa_desercion_por_asistencia.png" y mostrar.
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    plt.figure(figsize=(8, 5))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por cuartil de asistencia (Q1 = menor asistencia)")
    plt.ylabel("Tasa de deserción")
    plt.xlabel("Cuartil de asistencia")
    plt.xticks(rotation=0)
    plt.savefig(GRAFICOS / "tasa_desercion_por_asistencia.png", bbox_inches="tight")
    plt.show()
    plt.close()


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    # TODO 14: responder las cinco preguntas con groupby() y agg().
    print("\n" + "=" * 70)
    print("PASO 10: LAS CINCO PREGUNTAS")
    print("=" * 70)

    print("\nPregunta 1: ¿Qué programa presenta la tasa de deserción más alta?")
    p1 = (df.groupby("programa")
            .agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
            .sort_values("tasa", ascending=False))
    print(p1)
    print(f"-> Más alta: {p1.index[0]} ({p1['tasa'].iloc[0]:.1%}, {p1['estudiantes'].iloc[0]} estudiantes).")

    print("\nPregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?")
    p2 = df.groupby("beca").agg(tasa=("desertor", "mean"), estudiantes=("desertor", "size"))
    print(p2)
    print(f"-> Diferencia (no - sí): {(p2.loc['no', 'tasa'] - p2.loc['sí', 'tasa']) * 100:.1f} puntos porcentuales.")

    print("\nPregunta 3: ¿Qué jornada tiene el menor promedio acumulado?")
    p3 = (df.groupby("jornada")
            .agg(promedio=("promedio_acumulado", "mean"), estudiantes=("promedio_acumulado", "size"))
            .sort_values("promedio"))
    print(p3)
    print(f"-> Menor: {p3.index[0]} ({p3['promedio'].iloc[0]:.2f}, {p3['estudiantes'].iloc[0]} estudiantes).")

    print("\nPregunta 4: materias reprobadas promedio, desertores vs activos (sin graduados).")
    sin_graduados = df[df["estado"] != "graduado"]
    p4 = (sin_graduados.groupby("estado")
            .agg(reprobadas_promedio=("materias_reprobadas", "mean"), estudiantes=("materias_reprobadas", "size")))
    print(p4)
    # Los graduados no abandonaron ni siguen cursando: no pertenecen a ninguno de los dos grupos
    # comparados, y mezclarlos con los activos diluiría la diferencia real.

    print("\nPregunta 5: ¿La deserción aumenta conforme baja la asistencia?")
    p5 = (df.groupby("cuartil_asistencia", observed=True)
            .agg(tasa=("desertor", "mean"), asistencia_promedio=("asistencia_pct", "mean"),
                 estudiantes=("desertor", "size")))
    print(p5)
    print("-> Q1 es la asistencia más baja y Q4 la más alta.")


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
