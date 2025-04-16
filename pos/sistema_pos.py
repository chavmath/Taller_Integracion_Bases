import pyodbc
import datetime

# Configurar conexión con la base de datos
server = 'MATIAS'  
database = 'Taller3'  

# Conexión a SQL Server
conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes')
cursor = conn.cursor()

# Mostrar ventas con los títulos de las columnas
def mostrar_ventas():
    cursor.execute("SELECT * FROM VistaPOSProductosVentas")
    
    # Obtener los nombres de las columnas
    columns = [column[0] for column in cursor.description]
    
    # Imprimir los títulos de las columnas con un formato más limpio
    print("{:<15} {:<25} {:<15} {:<10} {:<15} {:<20} {:<15}".format(
        columns[0], columns[1], columns[2], columns[3], columns[4], columns[5], columns[6]
    ))  # Ajustar el ancho de las columnas
    
    # Imprimir los datos con alineación
    for row in cursor.fetchall():
        print("{:<15} {:<25} {:<15} {:<10} {:<15} {:<20} {:<15}".format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6]
        ))

# Registrar una venta y actualizar inventario
def registrar_venta(id_producto, cantidad_vendida, tienda_origen):
    fecha_venta = datetime.datetime.now()
    
    # Verificar si hay suficiente stock
    cursor.execute("""
        SELECT cantidad_disponible FROM Inventario WHERE id_producto_inv = ?
    """, id_producto)
    cantidad_disponible = cursor.fetchone()[0]
    
    if cantidad_disponible < cantidad_vendida:
        print(f"Error: No hay suficiente stock. Solo hay {cantidad_disponible} unidades disponibles.")
        return
    
    try:
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
    except Exception as e:
        print(f"Error al registrar la venta: {e}")
        conn.rollback()

# Menú del sistema POS
def menu_pos():
    while True:
        print("\nSistema de Punto de Venta (POS)")
        print("1. Mostrar ventas")
        print("2. Registrar venta")
        print("3. Salir")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            mostrar_ventas()
        elif opcion == "2":
            try:
                id_producto = int(input("ID del producto: "))
                cantidad_vendida = int(input("Cantidad vendida: "))
                tienda_origen = input("Tienda origen: ")
                registrar_venta(id_producto, cantidad_vendida, tienda_origen)
            except ValueError:
                print("Por favor, ingrese valores válidos para ID del producto y cantidad.")
        elif opcion == "3":
            break
        else:
            print("Opción no válida.")

menu_pos()
conn.close()
