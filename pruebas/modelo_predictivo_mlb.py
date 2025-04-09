import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# -------------------------------
# 1. Cargar datos desde Excel
# -------------------------------
archivo = "partidos_mlb.xlsx"  # Cambia por el nombre correcto si es necesario
df = pd.read_excel(archivo)

# -------------------------------
# 2. Filtrar solo partidos finalizados
# -------------------------------
df = df[df['estado'] == 'Final']

# -------------------------------
# 3. Crear variable objetivo
# -------------------------------
df['gana_local'] = (df['puntos_local'] > df['puntos_visitante']).astype(int)

# -------------------------------
# 4. Seleccionar variables del modelo
# -------------------------------
df_modelo = df[['puntos_local', 'puntos_visitante', 'gana_local']]

X = df_modelo[['puntos_local', 'puntos_visitante']]
y = df_modelo['gana_local']

# -------------------------------
# 5. Separar datos para entrenamiento y prueba
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -------------------------------
# 6. Entrenar el modelo
# -------------------------------
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# -------------------------------
# 7. Evaluar el modelo
# -------------------------------
y_pred = modelo.predict(X_test)
precision = accuracy_score(y_test, y_pred)
print(f"✅ Precisión del modelo: {precision:.2f}")

# -------------------------------
# 8. Predicción de ejemplo
# -------------------------------
nuevo_partido = pd.DataFrame({
    'puntos_local': [6],         # Cambia los valores como quieras
    'puntos_visitante': [4]
})
prediccion = modelo.predict(nuevo_partido)
print("\n🔮 ¿Gana el equipo local?:", "Sí 🏠" if prediccion[0] == 1 else "No 🚌")
