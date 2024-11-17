from flask import Flask, render_template, request
import csv
import networkx as nx
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

# Función para cargar los productos desde nuestro dataset 'Products.txt'
def cargar_productos():
    productos = []
    with open('Products.txt', 'r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            productos.append({
                "nombre": fila['product'],
                "category": fila['category'],
                "rating": float(fila['rating'])
            })
    return productos

# Cargar los productos al iniciar la aplicación
productos = cargar_productos()

# Función para graficar el grafo de recomendaciones
def graficar_grafo(recomendaciones, producto_ingresado):
    G = nx.Graph()
    G.add_node(producto_ingresado['nombre'], category=producto_ingresado['category'],
               rating=producto_ingresado['rating'])

    for producto in recomendaciones:
        G.add_node(producto['nombre'], category=producto['category'], rating=producto['rating'])
        G.add_edge(producto_ingresado['nombre'], producto['nombre'])

    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='gray')
    plt.title('Product Graph')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

# Función para sugerir productos utilizando DFS
def sugerir_productos_dfs(producto_nombre, num_recomendaciones=5):
    producto_ingresado = next((p for p in productos if producto_nombre.lower() in p['nombre'].lower()), None)

    if not producto_ingresado:
        return f"Producto '{producto_nombre}' no encontrado.", None

    grafo = {}
    for p in productos:
        if p['category'] not in grafo:
            grafo[p['category']] = []
        grafo[p['category']].append(p)

    stack = grafo[producto_ingresado['category']]
    visitados = set()
    productos_relacionados = []

    while stack:
        producto = stack.pop()
        if producto['nombre'] not in visitados:
            visitados.add(producto['nombre'])
            if producto['category'] == producto_ingresado['category'] and producto['nombre'] != producto_ingresado['nombre']:
                productos_relacionados.append(producto)

    productos_relacionados.sort(key=lambda x: x['rating'], reverse=True)
    recomendaciones = productos_relacionados[:num_recomendaciones]

    if recomendaciones:
        return recomendaciones, producto_ingresado
    else:
        return "No se encontraron productos relacionados.", producto_ingresado

# Ruta principal de la aplicación
@app.route('/', methods=['GET', 'POST'])
def index():
    sugerencia = []
    graph_image_base64 = None
    if request.method == 'POST':
        producto_nombre = request.form['producto']
        sugerencia, producto_ingresado = sugerir_productos_dfs(producto_nombre)
        if producto_ingresado:
            graph_image_base64 = graficar_grafo(sugerencia, producto_ingresado)
    return render_template('index.html', sugerencia=sugerencia, graph_image_base64=graph_image_base64)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)