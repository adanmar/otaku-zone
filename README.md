# Otaku Zone · tienda y gestión empresarial

Aplicación Flask con MariaDB/MySQL. La tienda y el centro de gestión comparten productos, clientes, pedidos e inventario.

## Ejecutar

Desde la raíz de `otaku-zone`:

```powershell
.\venv\Scripts\python.exe database\actualizar_negocio.py
.\venv\Scripts\python.exe app.py
```

Para una instalación nueva, crea primero la base con `database/otaku_zone.sql` y configura `config.py`. La migración agrega los módulos y puede ejecutarse de nuevo. Respaldar la base antes de cualquier actualización de esquema; MySQL confirma los cambios DDL por separado. El código está en la raíz del proyecto; `venv/` contiene únicamente el entorno y un lanzador compatible.

## Estructura

- `routes/`: controladores de tienda, cuentas y gestión.
- `services/business.py`: reglas de pedidos, pagos, compras y movimientos de inventario; transacciones y auditoría.
- `services/access.py`: permisos verificados contra la base en cada solicitud.
- `models/db.py`: conexión compartida.
- `database/enterprise_schema.py`: migración empresarial versionada.
- `templates/gestion/`: vistas del centro de gestión.
- `static/css/gestion.css`: sistema visual de administración.

## CRM

Expedientes de clientes, historial de compras, notas internas, solicitudes de atención y respuestas disponibles en la cuenta del cliente. Favoritos reales. Las consultas de visitantes se guardan, pero no generan correos automáticos ni acceso a la cuenta por coincidencia de email.

## SCM

Proveedores activos/inactivos, órdenes de compra con varias líneas, recepción completa, costo promedio ponderado, mínimos de reposición, ajustes por conteo físico y guías de envío. Una compra recibida no puede recibirse dos veces. La creación de la orden no cambia existencias.

## ERP

Pedidos con estados, registro comprobado de pagos y reembolsos, gastos, reportes por fechas, exportación CSV y bitácora de operaciones. El costo unitario de cada venta se conserva; las ventas históricas sin costo no producen un margen inventado.

## Permisos

| Perfil | Acceso |
| --- | --- |
| Administrador | Todas las áreas, usuarios y auditoría |
| Atención | CRM |
| Almacén | SCM y catálogo |
| Finanzas | ERP |
| Cliente | Tienda, sus pedidos, favoritos y solicitudes |

Una cuenta existente con rol `admin` conserva acceso como administrador. Los permisos del personal se asignan desde **Gestión → Usuarios y permisos**. No se crean usuarios ni contraseñas predeterminadas.

## Ciclo del pedido

1. El cliente registra el pedido: existencias reservadas y movimiento de salida.
2. Finanzas registra un pago comprobado; al cubrir el total puede confirmar el pedido.
3. Almacén prepara, registra guía y marca el envío.
4. Almacén confirma la entrega.
5. Antes del envío, se puede cancelar; si hay pagos, primero se registra su reembolso. La cancelación devuelve existencias una sola vez.

Los productos se archivan, conservando sus relaciones e historial. Los ajustes de inventario requieren motivo. Las respuestas internas y notas de operación no se muestran como parte del seguimiento público del pedido.

## Alcance de los datos

El inventario parte del saldo existente al activar la gestión. Antes de recibir mercancía de un producto con existencias, registra su costo inicial para calcular correctamente el promedio. Los costos antiguos desconocidos permanecen sin completar. Los pagos históricos no se infieren del estado del pedido. Completa costos y registra pagos solo con comprobantes reales.

El registro de pago/reembolso no mueve dinero en bancos ni pasarelas. Las guías son manuales y no consultan APIs de paqueterías. La recepción es completa; no incluye recepciones parciales. Los reportes son operativos y no sustituyen facturación fiscal, nómina o contabilidad legal. El flujo de entregas completadas no incluye devoluciones posteriores.

## Verificación

Probado con MariaDB local en una base aislada: permisos por área, CSRF, stock/costo al recibir, recepción duplicada, pedidos, pago previo a confirmación, envío con guía, cancelación/reembolso, propiedad de consultas/pedidos, favoritos, gastos, exportación y reconciliación del inventario. La base de pruebas se elimina al finalizar; no agrega operaciones ficticias a la base de negocio.

Para repetir las pruebas en una base aislada desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe tests\verify_workflows.py
```

La cuenta MySQL configurada debe poder crear y eliminar la base temporal de QA. Solo se elimina la base cuyo nombre generado empieza con `otaku_zone_qa_`.
