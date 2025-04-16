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

# Ver Auditoría de cambios en el estado de stock
def ver_auditoria_stock():
    cursor.execute("SELECT * FROM AuditoriaEstadoStock")
    
    # Obtener los nombres de las columnas
    columns = [column[0] for column in cursor.description]
    
    # Imprimir los títulos de las columnas con un formato limpio
    print("{:<15} {:<15} {:<20} {:<20}".format(  # Quitamos la fecha de cambio aquí
        columns[0], columns[1], columns[2], columns[3]
    ))  # Ajustar el ancho de las columnas
    
    # Imprimir los datos con alineación
    for row in cursor.fetchall():
        print("{:<15} {:<15} {:<20} {:<20}".format(
            row[0], row[1], row[2], row[3]
        ))

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

# Agregar cantidad al inventario de un producto
def agregar_cantidad_inventario():
    id_producto = int(input("ID del producto al que se le agregará cantidad: "))
    cantidad_agregada = int(input("Cantidad a agregar al inventario: "))
    
    # Actualizar la cantidad disponible del producto
    cursor.execute("""
        UPDATE Inventario
        SET cantidad_disponible = cantidad_disponible + ?
        WHERE id_producto_inv = ?
    """, cantidad_agregada, id_producto)
    
    # Registrar el cambio de estado en AuditoriaEstadoStock (sin incluir la fecha de cambio)
    cursor.execute("""
        INSERT INTO AuditoriaEstadoStock (id_producto, estado_anterior, nuevo_estado)
        SELECT id_producto_inv,
               estado_stock,
               CASE WHEN cantidad_disponible <= 0 THEN 'No hay stock' ELSE 'Disponible' END
        FROM Inventario
        WHERE id_producto_inv = ?
    """, id_producto)
    
    conn.commit()
    print(f"{cantidad_agregada} unidades agregadas al inventario del producto con ID {id_producto}.")

# Menú del sistema de inventario
def menu_inventario():
    while True:
        print("\nSistema de Inventario")
        print("1. Mostrar inventario")
        print("2. Actualizar precio")
        print("3. Agregar producto al inventario")
        print("4. Agregar cantidad al inventario")
        print("5. Ver Auditoría de Stock")
        print("6. Salir")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            mostrar_inventario()
        elif opcion == "2":
            id_producto = int(input("ID del producto: "))
            nuevo_precio = float(input("Nuevo precio: "))
            actualizar_precio(id_producto, nuevo_precio)
        elif opcion == "3":
            agregar_producto()
        elif opcion == "4":
            agregar_cantidad_inventario()
        elif opcion == "5":
            ver_auditoria_stock()
        elif opcion == "6":
            break
        else:
            print("Opción no válida.")

menu_inventario()
conn.close()
