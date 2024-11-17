from flask import Flask, render_template, request
import csv
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)

productos = []
with open('Products.txt', 'r', encoding='utf-8') as archivo:
    lector = csv.DictReader(archivo)
    for fila in lector:
        productos.append({
            "nombre": fila['product'],
            "category": fila['category'],
            "rating": float(fila['rating'])
        })
def graficar_grafo(grafo, filename='static/graph.png'):
    G = nx.Graph()

    for categoria, productos in grafo.items():
        for producto in productos:
            G.add_node(producto['nombre'], category=categoria, rating=producto['rating'])
            for otro_producto in productos:
                if producto != otro_producto:
                    G.add_edge(producto['nombre'], otro_producto['nombre'])

    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray')
    plt.title('Product Graph')
    plt.savefig(filename)
    plt.close()

def sugerir_productos_dfs(producto_nombre, num_recomendaciones=5):
    producto_ingresado = next((p for p in productos if producto_nombre.lower() in p['nombre'].lower()), None)

    if not producto_ingresado:
        return f"Producto '{producto_nombre}' no encontrado.", None

    # Crear un grafo de productos por categoría
    grafo = {}
    for p in productos:
        if p['category'] not in grafo:
            grafo[p['category']] = []
        grafo[p['category']].append(p)

    # Graficar el grafo y guardar la imagen
    graph_image_path = 'static/graph.png'
    graficar_grafo(grafo, graph_image_path)

    # DFS para buscar productos relacionados
    stack = grafo[producto_ingresado['category']]  # Empezamos con los productos de la misma categoría
    visitados = set()
    productos_relacionados = []

    while stack:
        producto = stack.pop()
        if producto['nombre'] not in visitados:
            visitados.add(producto['nombre'])
            if producto['category'] == producto_ingresado['category'] and producto['nombre'] != producto_ingresado['nombre']:
                productos_relacionados.append(producto)

    # Ordenar los productos por rating
    productos_relacionados.sort(key=lambda x: x['rating'], reverse=True)

    # Seleccionamos los primeros 'num_recomendaciones' productos
    recomendaciones = productos_relacionados[:num_recomendaciones]

    if recomendaciones:
        return recomendaciones, graph_image_path  # Regresamos la lista de productos recomendados y la ruta de la imagen
    else:
        return "No se encontraron productos relacionados.", graph_image_path
@app.route('/', methods=['GET', 'POST'])
def index():
    sugerencia = ""
    graph_image_path = None
    if request.method == 'POST':
        producto_nombre = request.form['producto']
        sugerencia, graph_image_path = sugerir_productos_dfs(producto_nombre)
    return render_template('index.html', sugerencia=sugerencia, graph_image_path=graph_image_path)

if __name__ == '__main__':
    app.run(debug=True)