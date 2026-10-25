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

## Consultas de autoridades y datos institucionales

- ¿Quién es el presidente del Banco Galicia?
- ¿Quiénes son los accionistas del Banco Macro?
- ¿Quién audita al Banco Supervielle?

## Consultas analíticas / rankings

Las responde `consultar_ranking.py`, que consulta a todas las entidades en paralelo (unos segundos).

- ¿Qué banco tiene más mora?
- ¿Cuáles son los 5 bancos con mayor cartera irregular?
- ¿Cuáles son los 5 bancos con más mora entre los 20 más grandes?
- ¿Los 3 bancos más grandes por activo?
- ¿Qué banco tiene más tarjetas de crédito emitidas?
- ¿Qué cuota de mercado tiene cada banco en tarjetas de crédito? ¿Y en depósitos?
- ¿Cuáles son los 10 bancos con más sucursales?
- ¿Qué banco tiene la mejor cobertura de previsiones?
- ¿Cuáles son los 5 bancos de menor ROE?
- ¿Cuántos bancos tienen mora mayor al 10%?
- ¿Qué compañía financiera tiene más préstamos?

## Consultas de totales del sistema y de grupos

- ¿Cuál es la mora promedio del sistema?
- ¿Cuántas tarjetas de crédito hay en total en el sistema financiero?
- ¿Cómo está la mora de los bancos públicos contra la de los privados?

## Consultas de evolución e historia (varios períodos)

Hasta 5 períodos salen de la API; para más, `consultar_historico.py` lee los PDF mensuales del BCRA, con historia completa desde 2014.

- ¿Cómo evolucionó la mora del Banco Galicia en el último año?
- ¿El activo del Banco Nación creció o cayó en los últimos meses?
- ¿Cómo viene la mora de consumo del sistema?
- ¿Cómo evolucionó la mora de consumo del Galicia desde 2018?
- ¿Cuánto creció en términos reales el patrimonio del Banco Macro en los últimos 24 meses? *(variación nominal ajustada con el IPC: cálculo propio)*
- ¿Cómo cambió el ROE del sistema año por año desde 2014?
- ¿Cuántas tarjetas de crédito tenía el Macro a fin de cada año desde 2019?

Las entidades que cambiaron de nombre no se encuentran en los PDF anteriores al cambio: por ejemplo, el Santander (antes Santander Río) en los PDF anteriores a junio de 2022 y el BBVA (antes BBVA Francés) en los anteriores a diciembre de 2019.

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

- ¿Cuántos clientes nuevos sumó el Banco X el mes pasado? *(el BCRA no publica altas de clientes; lo más cercano son las cajas de ahorro y los titulares de tarjetas)*
- ¿Cuántos usuarios tiene Mercado Pago? *(las billeteras virtuales no figuran en la nómina de entidades financieras del BCRA)*
- ¿Cuánto cotiza el dólar? *(fuera de las fuentes que consulta)*
- ¿Qué tasa paga el Banco Z en un plazo fijo hoy? *(publica tasa implícita promedio del período, no la tasa vigente de pizarra)*
- ¿Cuál era la mora del Banco Y en 2009? *(los PDF de 2010 y anteriores no se pueden leer; la historia completa empieza en 2014)*

## Notas sobre los períodos

Distintas fuentes tienen distintos rezagos:
- **Balance, indicadores, mora, situación de deudores y cuentas sueldo:** mensual, con unos 3 meses de rezago.
- **Sucursales y cajeros:** foto al último mes publicado.
- **Tarjetas, cuentas y empleados:** trimestral (marzo, junio, septiembre, diciembre), con unos 4 meses de rezago.
- **Medios de pago:** mensual; cada hoja del informe tiene su propio rezago.
- **Inflación:** mensual, se publica a mediados del mes siguiente.

Por eso, al preguntar por varios datos de un banco, las respuestas pueden corresponder a meses distintos. El oráculo siempre aclara a qué período pertenece cada dato.
