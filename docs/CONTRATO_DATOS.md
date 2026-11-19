# Contrato de datos — Dashboard ISO/IEC 38500:2024

El dashboard busca las hojas y columnas **por nombre exacto**. Este documento es
el acuerdo entre el Excel y `dashboard_ISO38500`: si se renombra una hoja o una
columna, hay que actualizar el código y este contrato al mismo tiempo.

## 1. Libro y hojas

| Elemento | Valor |
|---|---|
| Archivo | `Extraido_CIO_Completo.xlsx` |
| Origen | Google Drive, ID `15VJEg5OykTfv99NhHynsoqQfdea0ij2m` |
| Encabezados | Fila 1, salvo `Presupuesto proyect` (layout especial) |
| Hojas totales verificadas | 22 (versión del 2026-11-18) |

Hojas del libro: `Objetivos estrategicos`, `Pilares Estrategicos`,
`Presupuesto proyect`, `Iniciativas`, `Detalle iniciativa DVP`,
`Detalle iniciativa pmo`, `Indicadores Dominio TI`, `Riesgos`, `BSC`,
`Dominios Estrategicos`, `Cadena de valor`, `Arquitectura tecnologica`, `Dofa`,
`Porter`, `Resumen Ejecutivo`, `MAESTRA_INICIATIVAS`, `Calendario`,
`Gobierno de Datos`, `Gobierno IA`, `ISO 38500`, `ISO 38500 Evaluacion`,
`Plan de accion`.

> No todas las hojas son usadas por este dashboard. Las secciones 2 a 5
> describen las que sí se leen; `Pilares Estrategicos`, `Dominios Estrategicos`,
> `Cadena de valor`, `Resumen Ejecutivo` y `Calendario` no se usan directamente
> en la versión 1.0.0.

## 2. Hojas obligatorias

Sin estas hojas el dashboard no puede construir sus secciones principales.

### 2.1 `BSC`

| Columna | Tipo | Uso |
|---|---|---|
| `Perspectiva` | texto | Agrupación (Finance, Internal Process, Customers, etc.) |
| `Indicador` | texto | Nombre exacto; se usa para cruzar con ISO 38500 |
| `Actual` | número | Valor actual |
| `Meta` | número | Meta; no debe ser cero |

Verificado: 11 indicadores.

### 2.2 `Presupuesto proyect`

Layout especial:

- Una fila contiene encabezados `Presupuesto 2023`, `Presupuesto 2024`, etc.
- La primera columna contiene el tipo de iniciativa (`Iniciativas PMO`,
  `Iniciativas PPT`, `Iniciativas TD`, etc.).
- La fila de total (`Global Banco Unión`) se ignora y se recalcula.
- Los valores se convierten a formato largo: `Tipo`, `Año`, `Presupuesto`.

### 2.3 `Iniciativas`

El código toma las **primeras 7 columnas** y las renombra en este orden:

| Posición | Nombre esperado | Uso |
|---|---|---|
| 1 | `Siglas` | Llave para unir con PMO |
| 2 | `Nombre` | Se descarta en el merge |
| 3 | `Inicio LB` | Fecha de inicio línea base |
| 4 | `Fin LB` | Fecha de fin línea base |
| 5 | `Inicio Real` | Fecha de inicio real |
| 6 | `Fecha Acta Inicio` | Fecha de acta |
| 7 | `Fin Proyectado` | Fecha de fin proyectada |

### 2.4 `Detalle iniciativa DVP`

| Columna | Tipo | Uso |
|---|---|---|
| `Iniciativa- proyecto` | texto | Nombre de la iniciativa |
| `Categoria` | texto | Categoría / gerencia |
| `Tipo` | texto | Tipo de iniciativa |
| `RUPTURA` | texto | Ruptura estratégica |
| `OPM` | número | Prioridad OPM |
| `TIempo estimado alto nivel (semanas)` | número | Duración estimada |
| `Presupuesto Proyeectado` | número | Presupuesto (la errata es intencional) |

Verificado: 27 iniciativas.

### 2.5 `Detalle iniciativa pmo`

| Columna | Tipo | Uso |
|---|---|---|
| `ID` | número | Quita la fila de total (los totales no tienen ID) |
| `Siglas` | texto | Llave para unir con `Iniciativas` |
| `Iniciativa/Proyecto` | texto | Nombre |
| `Estado` | texto | Estado del proyecto |
| `MEGA` | texto | Meta grande; se usa para el principio Propósito |
| `Objetivo Estrategico` | texto | Se usa para el principio Estrategia |
| `Gerencia` | texto | Agrupación |
| `Sponsor` | texto | Rendición de cuentas |
| `Gerente` | texto | Rendición de cuentas |
| `Gestor` | texto | Informativo |
| `Año alocado` | número | Año |
| `PPTO PARA ROADMAP PPT` | número | Presupuesto |

Verificado: 26 proyectos + 1 fila de total.

### 2.6 `MAESTRA_INICIATIVAS`

| Columna | Tipo | Uso |
|---|---|---|
| `ID` | número | Identificador |
| `Sigla` | texto | Sigla |
| `Nombre` | texto | Nombre |
| `Tipo` | texto | `PMO`, `PPT`, `TD`, etc. |
| `Dominio` | texto | Dominio estratégico; `Por Clasificar` se trata como brecha |
| `CadenaValor` | texto | Cadena de valor |
| `Pilar` | texto | Pilar estratégico |

Verificado: 51 iniciativas.

### 2.7 `Riesgos`

| Columna | Tipo | Uso |
|---|---|---|
| `FRENTE` | texto | Frente tecnológico; celdas combinadas se rellenan hacia abajo |
| `COMPONENTE` | texto | Componente; celdas combinadas se rellenan hacia abajo |
| `RIESGOS` | texto | Descripción del riesgo |
| `IMPACTO` | texto | `Alto`, `Medio`, `Bajo` (se acepta `Moderado` como `Medio`) |

Verificado: 24 riesgos.

### 2.8 `Arquitectura tecnologica`

| Columna | Tipo | Uso |
|---|---|---|
| `Métrica` | texto | Nombre de la métrica (Aplicaciones, Servidores, etc.) |
| `Valor` | número | Valor de la métrica |

### 2.9 `Indicadores Dominio TI`

| Columna | Tipo | Uso |
|---|---|---|
| `INDICADOR` | texto | Nombre del indicador |
| Otras | texto/número | Fórmula, meta y demás columnas se muestran tal cual |

### 2.10 `Dofa`

| Columna | Tipo | Uso |
|---|---|---|
| `Tipo` | texto | `Fortaleza`, `Debilidad`, `Oportunidad`, `Amenaza` |
| `Descripción` | texto | Texto del análisis |

### 2.11 `Objetivos estrategicos`

Se usa en la sección de Gobierno de Datos para filtrar las filas que contienen
"Información" o "Analítica" en cualquier columna. No requiere un nombre de
columna específico, pero sí que la hoja exista.

### 2.12 `Porter`

Se muestra como tabla en la sección de Contexto. No requiere columnas
específicas.

## 3. Hojas ISO/IEC 38500:2024

### 3.1 `ISO 38500` (métricas oficiales)

| Columna | Tipo | Uso |
|---|---|---|
| `Principio` | texto | Nombre del principio (español o bilingüe) |
| `Sección` | texto | Sección de la norma (5.2 a 5.12) |
| `Tarea del modelo` | texto | Involucrar/Evaluar/Dirigir/Monitorear |
| `Resultado` | texto | Resultado de la sección 4.1 |
| `Métrica` | texto | Nombre de la métrica |
| `Fuente` | texto | Hoja o documento de origen |
| `Base en la norma` | texto | Referencia normativa |
| `Actual` | número | Valor actual |
| `Meta` | número | Meta |
| `Origen de la meta` | texto | De dónde sale la meta |
| `Menor es mejor` | `Sí`/`No` | Invierte el cálculo de cumplimiento |

Verificado: 19 métricas. Si esta hoja existe y tiene `Principio`, `Actual`,
`Meta` y `Menor es mejor`, el dashboard la usa en lugar de calcular las métricas.

### 3.2 `ISO 38500 Evaluacion` (evidencia de la sección 4.1)

| Columna | Tipo | Uso |
|---|---|---|
| `Sección` | texto | Sección de la norma |
| `Resultado` | texto | Resultado de la sección 4.1 |
| `Tema` | texto | `Datos`, `IA` o `TI` |
| `Punto` | texto | Punto evaluado |
| `Estado` | texto | `Con evidencia`, `Evidencia parcial`, `Sin evidencia` |
| `Evidencia` | texto | Evidencia encontrada en el banco |
| `Fuente de la evidencia` | texto | Hoja o documento |
| `Punto de la norma (texto original)` | texto | Texto original en inglés |

Verificado: 16 puntos.

> Compatibilidad: el código también acepta los encabezados antiguos
> `Traducción` y `Evidencia en el banco`; los renombra a `Punto` y `Evidencia`.

### 3.3 `Plan de accion`

| Columna | Tipo | Uso |
|---|---|---|
| `Principio` | texto | Principio con brecha |
| `Evaluar (Evaluate)` | texto | Descripción de la brecha |
| `Dirigir (Direct)` | texto | Acción en el portafolio |
| `Monitorear (Monitor)` | texto | Estado de la acción |
| `Origen` | texto | `DVP` o `PMO` |
| `Presupuesto` | número | Presupuesto de la acción |

Verificado: 3 acciones.

> Compatibilidad: si la hoja usa los encabezados `Brecha`,
> `Acción en el portafolio` y `Estado`, el código los renombra automáticamente.

## 4. Hojas de gobierno específicas

### 4.1 `Gobierno de Datos`

| Columna | Tipo | Uso |
|---|---|---|
| `Tipo de registro` | texto | `Iniciativa` o `Riesgo` |
| `Nombre` | texto | Nombre |
| `Hoja de origen` | texto | Hoja de donde proviene |
| `Categoría o componente` | texto | Categoría o componente |
| `Presupuesto` | número | Presupuesto |
| `Impacto` | texto | Solo para riesgos |
| `Estado` | texto | Estado de la iniciativa |

Verificado: 12 registros.

### 4.2 `Gobierno IA`

| Columna | Tipo | Uso |
|---|---|---|
| `Nombre` | texto | Nombre del caso o iniciativa |
| `Hoja de origen` | texto | Hoja de origen |
| `Categoría o gerencia` | texto | Categoría o gerencia |
| `Presupuesto` | número | Presupuesto |
| `Semanas` | número | Duración estimada |
| `Estado` | texto | Estado |

Verificado: 4 registros.

## 5. Hojas opcionales (aún no presentes)

Estas hojas permiten reemplazar cálculos por datos oficiales. Si no existen, la
sección correspondiente se muestra vacía o como pendiente; no se inventan datos.

### 5.1 `Inventario Datos`

`Dominio`, `Activo de datos`, `Clasificación`, `Responsable asignado`,
`Catalogado`, `Calidad %`, `Completitud %`.

### 5.2 `Inventario IA`

`Caso de uso`, `Área`, `Estado`, `Riesgo IA`, `Evaluación ética`, `Monitoreado`,
`Precisión %`.

### 5.3 `Operacion TI`

`Mes`, `Tipo`, `Canal`, `Cantidad`.

## 6. Vocabularios controlados

### 6.1 Principios ISO/IEC 38500:2024 (sección 5)

| Nombre en español | Sección |
|---|---|
| Propósito | 5.2 |
| Generación de valor | 5.3 |
| Estrategia | 5.4 |
| Supervisión | 5.5 |
| Rendición de cuentas | 5.6 |
| Involucramiento de partes interesadas | 5.7 |
| Liderazgo | 5.8 |
| Datos y decisiones | 5.9 |
| Gobierno del riesgo | 5.10 |
| Responsabilidad social | 5.11 |
| Viabilidad y desempeño en el tiempo | 5.12 |

### 6.2 Resultados del buen gobierno de TI (sección 4.1)

- Desempeño efectivo (*Effective performance*)
- Administración responsable (*Responsible stewardship*)
- Comportamiento ético (*Ethical behaviour*)

### 6.3 Tareas del modelo de gobierno (sección 6.2)

- Involucrar (*Engage stakeholders*)
- Evaluar (*Evaluate*)
- Dirigir (*Direct*)
- Monitorear (*Monitor*)

### 6.4 Otros vocabularios

| Campo | Valores esperados |
|---|---|
| Estado de métrica | `Cumple`, `Cerca`, `Bajo meta` |
| Estado de evidencia | `Con evidencia`, `Evidencia parcial`, `Sin evidencia` |
| Impacto de riesgo | `Alto`, `Medio`, `Bajo` |
| Tema de evaluación | `Datos`, `IA`, `TI` |
| Tipo de iniciativa | `PMO`, `PPT`, `TD` (según la maestra) |
| Estado de proyecto | `En proceso`, `No iniciado`, `Finalizado`, etc. |

## 7. Reglas de calidad aplicadas por el código

| Regla | Dónde se aplica |
|---|---|
| Recortar espacios en encabezados | `leer_hojas` |
| Eliminar columnas `Unnamed` | `leer_hojas` |
| Eliminar filas completamente vacías | `leer_hojas` |
| Aceptar coma decimal | `numero()` |
| Unificar `En Proceso` / `En proceso` | `pmo` |
| Unificar `Moderado` / `Medio` | `riesgos` |
| Rellenar celdas combinadas | `FRENTE` y `COMPONENTE` de riesgos |
| Ignorar fila de total de PMO | `ID` numérico |
| Recalcular total de presupuesto | Se ignora `Global Banco Unión` |
| Marcar `Por Clasificar` como brecha | `maestra`, ISO Estrategia |
| Reemplazar `#REF!` por nulo | PMO |
| No inventar datos faltantes | `hoja_opcional`, `agregar_metrica` |

## 8. Mapa hoja → sección del dashboard

| Hoja | Resumen | ISO 38500 | Datos | IA | Operación | BSC | Portafolio | Innovación | Riesgos | Arquitectura | Contexto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `BSC` | ✓ | ✓ |  | ✓ | ✓ | ✓ |  |  |  |  |  |
| `Presupuesto proyect` | ✓ |  |  |  |  |  |  |  |  |  |  |
| `Iniciativas` | ✓ | ✓ |  |  |  |  | ✓ |  |  |  |  |
| `Detalle iniciativa DVP` | ✓ | ✓ | ✓ | ✓ |  |  | ✓ | ✓ |  |  |  |
| `Detalle iniciativa pmo` | ✓ | ✓ |  |  |  |  | ✓ |  |  |  |  |
| `MAESTRA_INICIATIVAS` | ✓ | ✓ |  |  |  |  | ✓ |  |  | ✓ |  |
| `Riesgos` | ✓ |  | ✓ |  |  |  |  |  | ✓ |  |  |
| `Arquitectura tecnologica` |  |  |  |  | ✓ |  |  |  |  | ✓ |  |
| `Indicadores Dominio TI` |  |  |  |  | ✓ |  |  |  |  |  | ✓ |
| `Dofa` |  |  | ✓ |  |  |  |  |  |  |  | ✓ |
| `Porter` |  |  |  |  |  |  |  |  |  |  | ✓ |
| `Objetivos estrategicos` |  |  | ✓ |  |  |  |  |  |  |  |  |
| `ISO 38500` | ✓ | ✓ |  |  |  |  |  |  |  |  |  |
| `ISO 38500 Evaluacion` | ✓ | ✓ | ✓ | ✓ |  |  |  |  |  |  |  |
| `Plan de accion` |  | ✓ |  |  |  |  |  |  |  |  |  |
| `Gobierno de Datos` | ✓ |  | ✓ |  |  |  |  |  |  |  |  |
| `Gobierno IA` | ✓ |  |  | ✓ |  |  |  |  |  |  |  |

## 9. Cómo cambiar el contrato sin romper el dashboard

1. **No renombrar** hojas ni columnas existentes; agregar columnas nuevas al final.
2. Si es inevitable renombrar, actualizar el código y este documento en el mismo commit.
3. Mantener los encabezados en la fila 1 (excepto `Presupuesto proyect`).
4. Probar con la hoja llena, vacía y con valores nulos.
5. Actualizar el [CHANGELOG](../CHANGELOG.md) si el cambio afecta la versión.
