-- Creación de la base de datos
CREATE DATABASE Taller3
GO

-- Usar la base de datos
USE Taller3
GO

-- Crear tabla Productos
CREATE TABLE Productos (
    id_producto INT IDENTITY (1,1) PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    precio DECIMAL(10,2)
);

-- Crear tabla Inventario
CREATE TABLE Inventario (
    id_producto_inv INT,
    cantidad_disponible INT,
    ubicacion_tienda VARCHAR(100),
    estado_stock VARCHAR(50),
    FOREIGN KEY (id_producto_inv) REFERENCES Productos(id_producto)
);

-- Crear tabla Ventas
CREATE TABLE Ventas (
    id_venta INT IDENTITY(1,1) PRIMARY KEY,
    id_producto INT,
    cantidad_vendida INT,
    fecha_venta DATETIME,
    tienda_origen VARCHAR(100),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);

-- Crear tabla AuditoriaEstadoStock
CREATE TABLE AuditoriaEstadoStock (
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    id_producto INT,
    estado_anterior VARCHAR(50),
    nuevo_estado VARCHAR(50),
    fecha_cambio DATETIME DEFAULT GETDATE()
);

-- Trigger para actualizar el estado de stock
CREATE TRIGGER trg_ActualizarEstadoStock
ON Inventario
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE inv
    SET estado_stock = 
        CASE 
            WHEN inv.cantidad_disponible <= 0 THEN 'No hay stock'
            ELSE 'Disponible'
        END
    FROM Inventario inv
    INNER JOIN inserted i ON inv.id_producto_inv = i.id_producto_inv;

    -- Auditoría del cambio de estado
    INSERT INTO AuditoriaEstadoStock (id_producto, estado_anterior, nuevo_estado)
    SELECT 
        d.id_producto_inv,
        d.estado_stock,
        CASE 
            WHEN i.cantidad_disponible <= 0 THEN 'No hay stock'
            ELSE 'Disponible'
        END
    FROM inserted i
    JOIN deleted d ON i.id_producto_inv = d.id_producto_inv
    WHERE 
        d.estado_stock <> 
        CASE 
            WHEN i.cantidad_disponible <= 0 THEN 'No hay stock'
            ELSE 'Disponible'
        END;
END;

-- Trigger para registrar ventas
CREATE TRIGGER trg_RegistrarVenta
ON Ventas
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @id_producto INT, @cantidad_vendida INT, @tienda_origen VARCHAR(100);
    DECLARE @cantidad_disponible INT;

    DECLARE venta_cursor CURSOR FOR 
        SELECT id_producto, cantidad_vendida, tienda_origen FROM inserted;

    OPEN venta_cursor;

    FETCH NEXT FROM venta_cursor INTO @id_producto, @cantidad_vendida, @tienda_origen;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SELECT @cantidad_disponible = cantidad_disponible
        FROM Inventario
        WHERE id_producto_inv = @id_producto;

        IF @cantidad_disponible IS NULL
        BEGIN
            PRINT 'Producto no encontrado en inventario.';
        END
        ELSE
        BEGIN
            -- Asegurar que la cantidad disponible no sea negativa
            DECLARE @cantidad_a_vender INT = 
                CASE 
                    WHEN @cantidad_disponible >= @cantidad_vendida THEN @cantidad_vendida
                    ELSE @cantidad_disponible
                END;

            -- Insertar la venta ajustada con fecha actual
            INSERT INTO Ventas (id_producto, cantidad_vendida, fecha_venta, tienda_origen)
            VALUES (@id_producto, @cantidad_a_vender, GETDATE(), @tienda_origen);

            -- Actualizar inventario
            UPDATE Inventario
            SET cantidad_disponible = 
                CASE 
                    WHEN cantidad_disponible - @cantidad_a_vender < 0 THEN 0
                    ELSE cantidad_disponible - @cantidad_a_vender
                END
            WHERE id_producto_inv = @id_producto;
        END

        FETCH NEXT FROM venta_cursor INTO @id_producto, @cantidad_vendida, @tienda_origen;
    END;

    CLOSE venta_cursor;
    DEALLOCATE venta_cursor;
END;

-- Vista de inventario en el almacén
CREATE VIEW VistaInventarioAlmacen AS
SELECT 
    p.id_producto,
    p.nombre,
    i.cantidad_disponible,
    i.ubicacion_tienda,
    i.estado_stock
FROM Productos p
JOIN Inventario i ON p.id_producto = i.id_producto_inv;

-- Vista para el sistema POS (punto de venta)
CREATE VIEW VistaPOSProductosVentas AS
SELECT 
    p.id_producto AS "ID Producto",
    p.nombre AS "Nombre Producto",
    CONCAT('$', FORMAT(p.precio, 'C', 'en-US')) AS "Precio",  -- Formato con signo de dólar
    v.id_venta AS "ID Venta",
    v.cantidad_vendida AS "Cantidad Vendida",
    FORMAT(v.fecha_venta, 'yyyy-MM-dd HH:mm:ss') AS "Fecha Venta",  -- Formato de fecha
    v.tienda_origen AS "Tienda Origen"
FROM Productos p
JOIN Ventas v ON p.id_producto = v.id_producto;


-- Inserts con información modificada
INSERT INTO Productos (nombre, descripcion, precio)
VALUES 
('Smart TV LG 55"', 'Televisor 4K', 899.99),
('iPhone 14 Pro', 'Teléfono de gama premium', 1099.00),
('Teclado mecánico Razer', 'Teclado para gaming', 150.00);

INSERT INTO Inventario (id_producto_inv, cantidad_disponible, ubicacion_tienda, estado_stock)
VALUES 
(1, 15, 'Quito', 'Disponible'),
(2, 0, 'Guayaquil', 'No hay stock'),
(3, 40, 'Cuenca', 'Disponible');

-- Consultas de ejemplo
SELECT * FROM Productos;
SELECT * FROM Inventario;
SELECT * FROM Ventas;
SELECT * FROM AuditoriaEstadoStock;

SELECT * FROM VistaInventarioAlmacen;
SELECT * FROM VistaPOSProductosVentas;


-- Actualizar la tabla Inventario y auditar cambios de estado
UPDATE Inventario
SET cantidad_disponible = 5
WHERE id_producto_inv = 1;

-- Agregar constraint para evitar cantidades negativas en Inventario
ALTER TABLE Inventario
ADD CONSTRAINT chk_cantidad_disponible CHECK (cantidad_disponible >= 0);

