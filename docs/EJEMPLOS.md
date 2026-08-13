# Ejemplos de preguntas

Catálogo de preguntas que el oráculo sabe responder, organizadas por tipo. Todas se responden con datos reales extraídos de las fuentes oficiales en el momento de la consulta.

## Consultas puntuales (un banco, un dato)

- ¿Cuántas tarjetas de crédito tiene el Banco Galicia?
- ¿Cuántas cajas de ahorro tiene el Banco Nación?
- ¿Cuál es la mora del Banco Santander?
- ¿Cuál es el ROE del Banco Macro?
- ¿Cuánto es el activo total del Banco Provincia?
- ¿Cuántos empleados tiene el Banco Credicoop?
- ¿Cuántas sucursales tiene el BBVA?
- ¿Cuál es el apalancamiento del Banco Comafi?
- ¿Cuántos depósitos en plazo fijo tiene el Banco Ciudad?

## Consultas de varios datos de un mismo banco

- ¿Cuántas tarjetas de crédito y débito tiene el Galicia, y cuál es su mora?
- Dame el balance completo del Banco Nación: activo, préstamos, depósitos y patrimonio.
- ¿Cómo está el Banco Supervielle en mora de consumo vs comercial?

## Consultas analíticas / rankings

- ¿Qué banco tiene más mora?
- ¿Cuáles son los 5 bancos con mayor cartera irregular?
- ¿Los 3 bancos más grandes por activo?
- ¿Qué banco tiene más tarjetas de crédito emitidas?
- ¿Cuáles son los 10 bancos con más sucursales?
- ¿Qué banco tiene la mejor cobertura de previsiones?
- ¿Cuál es la mora promedio del sistema?
- ¿Cuántos bancos tienen mora mayor al 10%?

## Consultas de evolución (varios períodos)

- ¿Cómo evolucionó la mora del Banco Galicia en el último año?
- ¿El activo del Banco Nación creció o cayó en los últimos meses?
- ¿Cómo viene la mora de consumo del sistema?

## Consultas de inflación (INDEC)

- ¿Cuál fue la inflación de junio?
- ¿Cuánto acumula la inflación en 2026?
- ¿Cuál es la inflación de los últimos 12 meses?
- ¿Cuánto fue la inflación núcleo el último mes?
- ¿Qué rubro de la canasta subió más el último mes?
- ¿Cuánto subió Vivienda en los últimos 12 meses?

## Consultas de medios de pago (BCRA)

- ¿Cuántas transferencias se hicieron el último mes?
- ¿Cuál es el ticket promedio de las compras con tarjeta de crédito?
- ¿Cuántos cheques se rechazaron?

## Consultas cruzadas (mezclan fuentes)

- ¿El ticket promedio de crédito le ganó a la inflación el último mes?
- ¿La mora del sistema creció más rápido que la inflación?

## Ejemplos de "no se dispone del dato"

Estas preguntas el oráculo las responde diciendo que el dato no está disponible, sin inventar:

- ¿Cuántos clientes nuevos sumó el Banco X el mes pasado? *(el BCRA no publica altas de clientes)*
- ¿Cuál es la ganancia neta en pesos del Banco Y? *(publica indicadores de rentabilidad como ROE/ROA, no el resultado absoluto en todos los cortes)*
- ¿Cuánto cotiza el dólar? *(fuera de las fuentes que consulta)*
- ¿Qué tasa paga el Banco Z en un plazo fijo hoy? *(publica tasa implícita promedio del período, no la tasa vigente de pizarra)*

## Notas sobre los períodos

Distintas fuentes tienen distintos rezagos:
- **Balance, indicadores y mora:** mensual, el más actualizado.
- **Tarjetas, cuentas, sucursales:** trimestral (marzo, junio, septiembre, diciembre).
- **Inflación:** mensual, se publica a mediados del mes siguiente.

Por eso, al preguntar por varios datos de un banco, las respuestas pueden corresponder a meses distintos. El oráculo siempre aclara a qué período pertenece cada dato.
