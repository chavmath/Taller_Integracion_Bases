import pyodbc
import datetime

# Configurar conexión con la base de datos
server = 'MATIAS'  
database = 'Taller3'  

# Conexión a SQL Server
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = conn.cursor()

# Mostrar el inventario con los títulos de las columnas y formato limpio
def mostrar_inventario():
    cursor.execute("SELECT * FROM VistaInventarioAlmacen")
    
    # Obtener los nombres de las columnas
    columns = [column[0] for column in cursor.description]
    
    # Imprimir los títulos de las columnas con un formato limpio
    print("{:<15} {:<25} {:<20} {:<15}".format(
        columns[0], columns[1], columns[2], columns[3]
    ))  # Ajustar el ancho de las columnas
    
    # Imprimir los datos con alineación
    for row in cursor.fetchall():
        print("{:<15} {:<25} {:<20} {:<15}".format(
            row[0], row[1], row[2], row[3]
        ))

# Registrar una venta y actualizar inventario
def registrar_venta(id_producto, cantidad_vendida, tienda_origen):
    fecha_venta = datetime.datetime.now()
    
    # Insertar la venta en la tabla Ventas
    cursor.execute("""
        INSERT INTO Ventas (id_producto, cantidad_vendida, fecha_venta, tienda_origen)
        VALUES (?, ?, ?, ?)
    """, id_producto, cantidad_vendida, fecha_venta, tienda_origen)
    
    # Actualizar el inventario
    cursor.execute("""
        UPDATE Inventario
        SET cantidad_disponible = cantidad_disponible - ?
        WHERE id_producto_inv = ?
    """, cantidad_vendida, id_producto)
    
    conn.commit()
    print("Venta registrada y stock actualizado.")

# Actualizar el precio de un producto
def actualizar_precio(id_producto, nuevo_precio):
    cursor.execute("""
        UPDATE Productos
        SET precio = ?
        WHERE id_producto = ?
    """, nuevo_precio, id_producto)
    conn.commit()
    print("Precio actualizado.")

# Agregar un nuevo producto al inventario
def agregar_producto():
    nombre_producto = input("Nombre del producto: ")
    descripcion = input("Descripción del producto: ")
    precio = float(input("Precio del producto: "))
    cantidad_disponible = int(input("Cantidad disponible: "))
    ubicacion_tienda = input("Ubicación de la tienda: ")
    
    # Insertar el nuevo producto en la tabla Productos
    cursor.execute("""
        INSERT INTO Productos (nombre, descripcion, precio)
        VALUES (?, ?, ?)
    """, nombre_producto, descripcion, precio)
    
    # Obtener el id del último producto insertado
    cursor.execute("SELECT MAX(id_producto) FROM Productos")
    id_producto = cursor.fetchone()[0]
    
    # Insertar el inventario del producto
    cursor.execute("""
        INSERT INTO Inventario (id_producto_inv, cantidad_disponible, ubicacion_tienda, estado_stock)
        VALUES (?, ?, ?, ?)
    """, id_producto, cantidad_disponible, ubicacion_tienda, "Disponible")
    
    conn.commit()
    print("Producto agregado al inventario.")

# Menú del sistema de inventario
def menu_inventario():
    while True:
        print("\nSistema de Inventario")
        print("1. Mostrar inventario")
        print("2. Registrar venta")
        print("3. Actualizar precio")
        print("4. Agregar producto al inventario")
        print("5. Salir")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            mostrar_inventario()
        elif opcion == "2":
            id_producto = int(input("ID del producto: "))
            cantidad_vendida = int(input("Cantidad vendida: "))
            tienda_origen = input("Tienda origen: ")
            registrar_venta(id_producto, cantidad_vendida, tienda_origen)
        elif opcion == "3":
            id_producto = int(input("ID del producto: "))
            nuevo_precio = float(input("Nuevo precio: "))
            actualizar_precio(id_producto, nuevo_precio)
        elif opcion == "4":
            agregar_producto()
        elif opcion == "5":
            break
        else:
            print("Opción no válida.")

menu_inventario()
conn.close()
