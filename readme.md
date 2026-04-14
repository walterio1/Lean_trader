TODO: 
correr buy-and-hold -> Ok
crear algo un poco más sofisticado (pº vs mm) -> OK
entrar datos históricos aqui: sp y vix minuto a minuto : es_full_1_min; vix_full_1_min; 
(variable de estado (diaria) - carpeta futuros vix: asimismo, diario: vix estructura a término - complejo) 
crear modelo aqui con datos históricos
más adelante incorporar el desarrollo del modelo sp500-vix en Lean

# SP500 - VIX Strategy
CONCEPTO Proyecto intraday con sp500 ayudado por vix

1 - Crear una variable “estado” del mercado que discrimine el momento bajo el supuesto de que el precio reacciona distinto a varios inputs según en qué estado esté el mercado.
La variable estado para el sp500 vendrá dada por dos variables de apoyo:
    • Diaria: Estructura a término del vix (alcista o bajista entre 1º y 2º futuros del vix), dada por las series diarias del vix (se mantiene para toda la sesión) - valor del cierre del día anterior.
    (Nota: la diaria también podría ser 4: vix sube/baja y sp500 sube/baja en la sesión anterior)
    • Intraday Subida o bajada reciente (intraday – puede ser de 1 min, 1 hr, mm, etc) del vix (front contract) combinada con subida o bajada en el mismo periodo del sp500. Caben por ello cuatro casos.
        ◦ Han subido ambos
        ◦ Han bajado ambos
        ◦ Ha subido el vix y bajado el sp500
        ◦ Ha bajado el vix y subido el sp500
Con la discriminación de la variable de estado tenemos 8 casos: los cuatro anteriores tanto para estructura alcista del vix como para estructura bajista.
En cada estado evaluamos la bondad de diversas estrategias, por ejemplo:
    • Precio contra media (sería la que recoja el último pico y valle)
    • Autorregresivo con 1 obs de decalaje
    • Compra venta según haga el vix, ya sea up/dn del vix previo, o precio contra media del vix
    
Por qué intraday y no diario? Porque necesitamos muestras grandes, y en diario no son suficientes. Lo serían si lo hacemos para muchos valores individuales (se amplía la muestra por múltiples series, ya que no por mayor granularidad del periodo)

## TODO List

- Entrar tres variables en la simulación. 
- Preparar una de las tres variables (estructura a término) diaria.
