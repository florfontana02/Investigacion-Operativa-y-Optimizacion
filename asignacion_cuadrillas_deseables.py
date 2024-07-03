import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass
import time

TOLERANCE =10e-6 
Orden = recordclass('Orden', 'id beneficio cant_trab')

class InstanciaAsignacionCuadrillas:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        
    def leer_datos(self,nombre_archivo):

        # Se abre el archivo
        f = open(nombre_archivo)

        # Lectura cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Lectura cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Lectura de las ordenes
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            linea = f.readline().rstrip().split(' ')
            self.ordenes.append(Orden(linea[0],linea[1],linea[2]))
        
        # Lectura cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Lectura conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            linea = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Lectura ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            linea = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Lectura ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            linea = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,linea)))
        
        # Lectura cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Lectura ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            linea = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,linea)))
        
        # Se cierra el archivo de entrada
        f.close()


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada 	
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaAsignacionCuadrillas()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    # Definir y agregar las variables:
	# metodo 'add' de 'variables', con parametros:
	# obj: costos de la funcion objetivo
	# lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)
	
    T = instancia.cantidad_trabajadores
    O = instancia.cantidad_ordenes
    K = 6 # Días hábiles
    L = 5 # Turnos por día 

    # Llenar coef\_funcion\_objetivo
    coeficientes_funcion_objetivo = []

    # Poner nombre a las variables
    nombres = []
    tipos = []

    
    # Variables delta_ij
    for i in range(T):
        for j in range(O):
            coeficientes_funcion_objetivo.append(0.0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"delta_{i}_{j}")
            tipos.append('B')

    # Variables alfa_jkl
    for j in range(O):
        for k in range(K):
            for l in range(L):
                coeficientes_funcion_objetivo.append(float(instancia.ordenes[j].beneficio)) 
                nombres.append(f"alfa_{j}_{k}_{l}")
                tipos.append('B')

    # Variables beta_ijkl
    for i in range(T):
        for j in range(O):
            for k in range(K):
                for l in range(L):
                    coeficientes_funcion_objetivo.append(0.0)  # 0 porque no esta en la funcion objetivo
                    nombres.append(f"beta_{i}_{j}_{k}_{l}")
                    tipos.append('B')

    # Variables omega_ik
    for i in range(T):
        for k in range(K):
            coeficientes_funcion_objetivo.append(0.0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"omega_{i}_{k}")
            tipos.append('B')
    
    # Variables gamma_i^n
    for i in range(T):
        for n in range(1, 4):
            coeficientes_funcion_objetivo.append(0.0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"gamma_{i}_{n}")
            tipos.append('B')

    # Variables epsilon_ii*j
    for (i,i_) in instancia.conflictos_trabajadores:
        for j in range(O):
            coeficientes_funcion_objetivo.append(-1000.0)
            nombres.append(f"psilon_{i}_{i_}_{j}")
            tipos.append('B')

    # Variables mu_ijj*
    for i in range(T):
        for (j,j_) in instancia.ordenes_repetitivas:
            coeficientes_funcion_objetivo.append(-1000.0)
            nombres.append(f"mu_{i}_{j}_{j_}")
            tipos.append('B')

    # Variables c_i_n
    for i in range(T):
        for n in range(1,5): 
            coeficientes_funcion_objetivo.append(-1000.0 * (n == 1) - 1200.0 * (n == 2) - 1400.0 * (n == 3) - 1500.0 * (n == 4))  
            nombres.append(f"c_{i}_{n}")
            tipos.append('I')

 

    # Variables z y w (max y min)
    coeficientes_funcion_objetivo.append(-0.00005)
    coeficientes_funcion_objetivo.append(0.00005)
    nombres.append("z")
    nombres.append("w")
    tipos.append('I')
    tipos.append('I')
 
    lb = [0] * (len(coeficientes_funcion_objetivo)) 
    ub = [1] * (len(coeficientes_funcion_objetivo)-(4*T+2))
    ub.extend([O] * ((4 * T)+2))

    
    # Agregar las variables
    prob.variables.add(obj=coeficientes_funcion_objetivo, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    # Agregar las restricciones ax <= (>= ==) b:
	# funcion 'add' de 'linear_constraints' con parametros:
	# lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)
	
    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.
    T = instancia.cantidad_trabajadores
    O = instancia.cantidad_ordenes
    K = 6 # Días hábiles
    L = 5 # Turnos por día

    restricciones = []
    sentidos = []
    rhs = []
    nombres = []

  #restriccion de que si realizo la orden j, me aseguro que tenga los t_j trabajadores que requiere
    for j in range(O):
        indices = []
        valores = []
        for i in range(T):
            indices.append(f"delta_{i}_{j}")
            valores.append(1)
        for k in range(K):
            for l in range(L):
              indices.append(f"alfa_{j}_{k}_{l}")
              valores.append(-float(instancia.ordenes[j].cant_trab))
        fila = [indices, valores]
        restricciones.append(fila)
        sentidos.append('E') 
        rhs.append(0)  
        nombres.append(f"trabajadores_necesarios_orden_{j}")  

#Agrego las restriccion de que una orden se realiza en un solo turno, una sola vez
    for j in range(O):
        indices = []
        valores = []
        for k in range(K):
            for l in range(L):
              indices.append(f"alfa_{j}_{k}_{l}")
              valores.append(1)
        fila = [indices, valores]
        restricciones.append(fila)
        sentidos.append('L')  # 'L' para menor o igual
        rhs.append(1)
        nombres.append(f"la orden {j} se realiza en un solo turno, una sola vez")
   
   #Ningun trabajador hace dos ordenes al mismo tiempo. Usamos linealizacion
      # Restriccion 1
    for i in range(T):
      for j in range(O):
        for k in range(K):
          for l in range(L):
            indices = [f"delta_{i}_{j}",f"alfa_{j}_{k}_{l}",f"beta_{i}_{j}_{k}_{l}"]
            valores = [1,1,-1]
            fila = [indices, valores]
            restricciones.append(fila)
            sentidos.append('L')  # 'L' para menor o igual
            rhs.append(1)
            nombres.append("ningun trabajador hace dos ordenes al mismo tiempo (restriccion 1)")

      # Restriccion 2
    for i in range(T):
      for j in range(O):
        for k in range(K):
          for l in range(L):
            indices = [f"delta_{i}_{j}",f"alfa_{j}_{k}_{l}",f"beta_{i}_{j}_{k}_{l}"]
            valores = [-1,-1,2]
            fila = [indices, valores]
            restricciones.append(fila)
            sentidos.append('L')  # 'L' para menor o igual
            rhs.append(0)
            nombres.append("ningun trabajador hace dos ordenes al mismo tiempo (restriccion 2)")

      # Restriccion 3
    for i in range(T):
      for k in range(K):
        for l in range(L):
          indices = []
          valores = []
          for j in range(O):
            indices.append(f"beta_{i}_{j}_{k}_{l}")
            valores.append(1)
          fila = [indices, valores]
          restricciones.append(fila)
          sentidos.append('L')  # 'L' para menor o igual
          rhs.append(1)
          nombres.append("ningun trabajador hace dos ordenes al mismo tiempo (restriccion 3)")
# Ningun trabajador puede trabajar los 6 dias de la semana
      # Restriccion 1
    for i in range(T):
      for k in range(K):
        indices = [f"omega_{i}_{k}"]
        valores = [-1]
        for l in range(L):
          for j in range(O):
            indices.append(f"beta_{i}_{j}_{k}_{l}")
            valores.append(1/5)
        fila = [indices, valores]
        restricciones.append(fila)
        sentidos.append('L')  # 'L' para menor o igual
        rhs.append(0)
        nombres.append("Ningun trabajador puede trabajar los 6 dias de la semana (restriccion 1)")
        
        # Restriccion 2
    for i in range(T):
      for k in range(K):
        indices = [f"omega_{i}_{k}"]
        valores = [-1]
        for l in range(L):
          for j in range(O):
            indices.append(f"beta_{i}_{j}_{k}_{l}")
            valores.append(1)
        fila = [indices, valores]
        restricciones.append(fila)
        sentidos.append('G')
        rhs.append(0)
        nombres.append("Ningun trabajador puede trabajar los 6 dias de la semana (restriccion 2)")
  
        # Restriccion 3
    for i in range(T):
      indices = []
      valores = []
      for k in range(K):
        indices.append(f"omega_{i}_{k}")
        valores.append(1)
      fila = [indices, valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(5)
      nombres.append("Ningun trabajador puede trabajar los 6 dias de la semana (restriccion 3)")
    # Ningun trabajador puede trabajar los 5 turnos en un dia
    for i in range(T):
      for k in range(K):
        indices = []
        valores = []
        for l in range(L):
          for j in range(O):
            indices.append(f"beta_{i}_{j}_{k}_{l}")
            valores.append(1)
        fila = [indices,valores]
        restricciones.append(fila)
        sentidos.append('L')
        rhs.append(4)
        nombres.append("Ningun trabajador puede trabajar los 5 turnos en un dia")
      
      # Órdenes que no pueden ser resueltas en turnos consecutivos por un trabajador
    for (j,j_) in instancia.ordenes_conflictivas:
      # Restriccion 1
      for i in range(T):
        for k in range(K):
          for l in range(L-1):
            indices = [f"beta_{i}_{j}_{k}_{l}",f"beta_{i}_{j_}_{k}_{l+1}"]
            valores = [1,1]
            fila = [indices,valores]
            restricciones.append(fila)
            sentidos.append('L')
            rhs.append(1)
            nombres.append(f"Restriccion de orden conflictiva {j} con {j_} (restriccion 1)")
      #Restriccion 2
      for i in range(T):
        for k in range(K):
          for l in range(L-1):
            indices = [f"beta_{i}_{j_}_{k}_{l}",f"beta_{i}_{j}_{k}_{l+1}"]
            valores = [1,1]
            fila = [indices,valores]
            restricciones.append(fila)
            sentidos.append('L')
            rhs.append(1)
            nombres.append(f"Restriccion de orden conflictiva {j} con {j_} (restriccion 2)")
 
  # Orden con ti trabajadores asignados en un mismo turno
    for j in range(O):
       for k in range(K):
          for l in range(L):
            indices = [f"alfa_{j}_{k}_{l}"]
            valores = [-float(instancia.ordenes[j].cant_trab)]
            for i in range(T):
              indices.append(f"beta_{i}_{j}_{k}_{l}")
              valores.append(1)
            fila = [indices,valores]
            restricciones.append(fila)
            sentidos.append('E')
            rhs.append(0)
            nombres.append(f"Orden {i} con t_{i} trabajadores asignados en el mismo turno")
  
  # Diferencia entre trabajador que mas y menos tareas realizaron menor a 8

# defino maximo z
    for i in range(T):
      indices = ["z"]
      valores = [1]
      for j in range(O):
        indices.append(f"delta_{i}_{j}")
        valores.append(-1)
      fila = [indices, valores]
      restricciones.append(fila)
      sentidos.append('G')
      rhs.append(0)
      nombres.append(f"Defino_z_max_con_{i}") 

  # defino minimo w
    for i in range(T):
      indices = ["w"]
      valores = [1]
      for j in range(O):
        indices.append(f"delta_{i}_{j}")
        valores.append(-1)
      fila = [indices, valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(0)
      nombres.append(f"Defino_w_min_con_{i}") 

  # restriccion de que la diferencia no sea mayor a 8

    indices = ["z","w"]
    valores = [1,-1]
    fila = [indices, valores]
    restricciones.append(fila)
    sentidos.append('L')
    rhs.append(8)
    nombres.append(f"max-min_menor_8") 

    # Sueldo
    # Restriccion 1
    for i in range(T):
      # 5 * gamma_i^1 <= c_i^1
      indices = [f"gamma_{i}_1", f"c_{i}_1"]
      valores = [-5,1]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('G')
      rhs.append(0)
      nombres.append(f"Sueldo_(restriccion_1.1)_{i}")
      
      # c_i^1 <= 5
      indices = [f"c_{i}_1"]
      valores = [1]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(5)
      nombres.append(f"Sueldo_(restriccion_1.2)_{i}")

    # Restriccion 2
    for i in range(T):
      # 5 * gamma_i^2 <= c_i^2
      indices = [f"gamma_{i}_2", f"c_{i}_2"]
      valores = [-5,1]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('G')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 2.1)_{i}")

      # c_i^2 <= 5 * gamma_i^1
      indices = [f"c_{i}_2", f"gamma_{i}_1"]
      valores = [1, -5]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 2.2)_{i}")

    # Restriccion 3
    for i in range(T):
      # 5 * gamma_i^3 <= c_i^3
      indices = [f"gamma_{i}_3", f"c_{i}_3"]
      valores = [-5,1]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('G')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 3.1)_{i}")
      
      # c_i^3 <= 5 * gamma_i^2
      indices = [f"c_{i}_3", f"gamma_{i}_2"]
      valores = [1, -5]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 3.2)_{i}")

    # Restriccion 4
    for i in range(T):
      indices = [f"c_{i}_4",f"gamma_{i}_3"]
      valores = [1, -O]
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('L')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 4)_{i}")
    
    # Restriccion 5

    for i in range(T):
      indices = []
      valores = []
      for n in range(1,5):
        indices.append(f"c_{i}_{n}")
        valores.append(1)
      for j in range(O):
        indices.append(f"delta_{i}_{j}")
        valores.append(-1)
      fila = [indices,valores]
      restricciones.append(fila)
      sentidos.append('E')
      rhs.append(0)
      nombres.append(f"Sueldo (restriccion 5)_{i}")
        

  # Ordenes correlativas
    for (j,j_) in instancia.ordenes_correlativas:
      for k in range(K):
        for l in range(L-1): #Agrego -1 para que no se vaya de rango
          indices = [f"alfa_{j}_{k}_{l}",f"alfa_{j_}_{k}_{l+1}"]
          valores = [1,-1]
          fila = [indices,valores]
          restricciones.append(fila)
          sentidos.append('L')
          rhs.append(0)
          nombres.append(f"Restriccion de orden correlativa {j} con {j_}")

  # Deseables 
  # Conflictos entre trabajadores
      for j in range(O):
          for (i, i_) in instancia.conflictos_trabajadores :  
              # Restricción 1
              indices = [f"psilon_{i}_{i_}_{j}", f"delta_{i}_{j}", f"delta_{i_}_{j}"]
              valores = [2, -1, -1]
              fila = [indices, valores]
              restricciones.append(fila)
              sentidos.append('L')  # 'L' para menor o igual
              rhs.append(0)
              nombres.append(f"conflicto_trabajadores_(restriccion_1)_{i}_{i_}_{j}")
              
              # Restricción 2
              indices = [f"psilon_{i}_{i_}_{j}", f"delta_{i}_{j}", f"delta_{i_}_{j}"]
              valores = [-1, 1, 1]
              fila = [indices, valores]
              restricciones.append(fila)
              sentidos.append('L')  # 'L' para menor o igual
              rhs.append(1)
              nombres.append(f"conflicto_trabajadores_(restriccion_2)_{i}_{i_}_{j}")

# Pares de órdenes repetitivas
    for (j,j_) in instancia.ordenes_repetitivas:
        for i in range(T) :  
            # Restricción 1
            indices = [f"mu_{i}_{j}_{j_}", f"delta_{i}_{j}", f"delta_{i}_{j_}"]
            valores = [2, -1, -1]
            fila = [indices, valores]
            restricciones.append(fila)
            sentidos.append('L')  # 'L' para menor o igual
            rhs.append(0)
            nombres.append(f"ordenes_repetitivas_(restriccion_1)_{i}_{j}_{j_}")
            
            # Restricción 2
            indices = [f"mu_{i}_{j}_{j_}", f"delta_{i}_{j}", f"delta_{i}_{j_}"]
            valores = [-1, 1, 1]
            fila = [indices, valores]
            restricciones.append(fila)
            sentidos.append('L')  # 'L' para menor o igual
            rhs.append(1)
            nombres.append(f"ordenes_repetitivas_(restriccion_2)_{i}_{i}_{j_}")



    prob.linear_constraints.add(lin_expr=restricciones, senses=sentidos, rhs=rhs, names=nombres)

def armar_lp(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.maximize)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
    prob.parameters.mip.tolerances.mipgap.set(1e-10) #por ejemplo
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    nombres = prob.variables.get_names()
    valores_variables = prob.solution.get_values()

    tolerancia = 1e-5
    for i in range(len(valores_variables)):
      if valores_variables[i] > tolerancia:
        print(f"{nombres[i]} = {valores_variables[i]}")

def main():
    
    start = time.time()

    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob,instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

    end = time.time()
    total_time = end - start
    total_minutes = total_time / 60
    print(f"Tiempo de ejecucion: {total_minutes:.2f} minutos")

if __name__ == '__main__':
    main()

