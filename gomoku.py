import random
import time


class Player:
    """
    Clase que representa un jugador (humano o IA).
    """
    def __init__(self, symbol, ai_type=None):
        """
        Inicializa un jugador.
        :param symbol: Símbolo del jugador ('X' o 'O').
        :param ai_type: Tipo de IA ('random', 'greedy', 'worst', 'expert') o None para jugador humano.
        """
        self.symbol = symbol
        self.ai_type = ai_type  # Tipo de IA o None si es humano


class Gomoku:
    """
    Clase principal para manejar el juego de Gomoku.
    """
    def __init__(self, board_size=15, win_length=5, ai_time_limit=2):
        """
        Inicializa el juego.
        :param board_size: Tamaño del tablero (default 15x15).
        :param win_length: Número de fichas consecutivas necesarias para ganar.
        :param ai_time_limit: Tiempo máximo en segundos para que la IA tome una decisión.
        """
        self.board_size = board_size
        self.win_length = win_length
        self.ai_time_limit = ai_time_limit
        self.board = [['.' for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = None
        self.nodes_expanded = 0  # Contador de nodos expandidos

    def print_board(self):
        """
        Imprime el tablero con etiquetas de filas y columnas.
        """
        print("   " + " ".join([chr(65 + i) for i in range(self.board_size)]))  # Etiquetas de columnas
        for i, row in enumerate(self.board):
            print(f"{i + 1:2} " + " ".join(row))  # Etiquetas de filas
        print("\n")

    def is_valid_move(self, row, col):
        """
        Verifica si un movimiento es válido.
        :param row: Fila del tablero.
        :param col: Columna del tablero.
        :return: True si la celda está vacía y dentro de los límites del tablero.
        """
        return 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == '.'

    def make_move(self, player, row, col):
        """
        Realiza un movimiento en el tablero si es válido.
        :param player: Jugador que realiza el movimiento.
        :param row: Fila donde se realiza el movimiento.
        :param col: Columna donde se realiza el movimiento.
        :return: True si el movimiento fue exitoso, False de lo contrario.
        """
        if self.is_valid_move(row, col):
            self.board[row][col] = player.symbol
            return True
        return False

    def check_win(self, player):
        """
        Verifica si el jugador actual ha ganado.
        :param player: Jugador cuyo símbolo se verifica.
        :return: True si el jugador ha ganado, False de lo contrario.
        """
        symbol = player.symbol
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Revisa todas las direcciones posibles
                if (self.check_direction(row, col, 1, 0, symbol) or  # Horizontal
                    self.check_direction(row, col, 0, 1, symbol) or  # Vertical
                    self.check_direction(row, col, 1, 1, symbol) or  # Diagonal \
                    self.check_direction(row, col, 1, -1, symbol)):  # Diagonal /
                    return True
        return False

    def check_direction(self, row, col, row_delta, col_delta, symbol):
        """
        Verifica si hay una secuencia de fichas consecutivas en una dirección.
        :param row: Fila inicial.
        :param col: Columna inicial.
        :param row_delta: Incremento de fila para avanzar.
        :param col_delta: Incremento de columna para avanzar.
        :param symbol: Símbolo del jugador a verificar.
        :return: True si hay una secuencia ganadora, False de lo contrario.
        """
        count = 0
        for _ in range(self.win_length):
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == symbol:
                count += 1
                row += row_delta
                col += col_delta
            else:
                break
        return count == self.win_length

    def is_full(self):
        """
        Verifica si el tablero está lleno.
        :return: True si no hay espacios vacíos, False de lo contrario.
        """
        return all('.' not in row for row in self.board)

    def evaluate_board(self, symbol):
        """
        Evalúa el estado del tablero basándose en 5 heurísticas:
        1. Longitud de alineaciones propias.
        2. Bloqueo de alineaciones del oponente.
        3. Control del centro del tablero.
        4. Espacios libres adyacentes.
        5. Potencial de extensión para formar alineaciones.
        :param symbol: Símbolo del jugador evaluado.
        :return: Puntuación del tablero desde la perspectiva del jugador.
        """
        opponent_symbol = 'X' if symbol == 'O' else 'O'
        score = 0
        center = self.board_size // 2

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == symbol:
                    # Heurística 1: Longitud de alineaciones propias
                    score += self.count_aligned(row, col, symbol)
                    # Heurística 3: Control del centro
                    score += max(0, 5 - (abs(row - center) + abs(col - center)))
                    # Heurística 4: Espacios libres adyacentes
                    score += self.count_adjacent_spaces(row, col)
                    # Heurística 5: Potencial de extensión
                    score += self.potential_extension(row, col, symbol)
                elif self.board[row][col] == opponent_symbol:
                    # Heurística 2: Bloqueo de alineaciones del oponente
                    score -= self.count_aligned(row, col, opponent_symbol)
        return score

    def count_aligned(self, row, col, symbol):
        """
        Cuenta alineaciones de fichas en torno a una celda.
        :param row: Fila inicial.
        :param col: Columna inicial.
        :param symbol: Símbolo a evaluar.
        :return: Número de alineaciones propias u oponentes.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        count = 0
        for dr, dc in directions:
            for i in range(-self.win_length + 1, self.win_length):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == symbol:
                    count += 1
        return count

    def count_adjacent_spaces(self, row, col):
        """
        Cuenta celdas vacías alrededor de una posición.
        :param row: Fila de la celda.
        :param col: Columna de la celda.
        :return: Número de celdas vacías adyacentes.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1), (-1, -1), (-1, 1), (-1, 0), (0, -1)]
        count = 0
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == '.':
                count += 1
        return count

    def potential_extension(self, row, col, symbol):
        """
        Evalúa el potencial de formar alineaciones mayores desde una celda.
        :param row: Fila de la celda.
        :param col: Columna de la celda.
        :param symbol: Símbolo a evaluar.
        :return: Potencial de extensión.
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        potential = 0
        for dr, dc in directions:
            for i in range(-self.win_length + 1, self.win_length):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.board_size and 0 <= c < self.board_size:
                    if self.board[r][c] == symbol or self.board[r][c] == '.':
                        potential += 1
        return potential

    def play(self):
        """
        Inicia el juego. Permite configurar jugadores como humanos o IA.
        """
        print("Configuración del juego Gomoku")
        self.ai_time_limit = float(input("Ingrese el tiempo máximo para las decisiones de la IA (en segundos): "))

        # Configuración de los jugadores
        print("\nSeleccione el tipo de cada jugador:")
        player1_type = input("Jugador 1 (X) [human/random/greedy/worst/expert]: ").strip().lower()
        player2_type = input("Jugador 2 (O) [human/random/greedy/worst/expert]: ").strip().lower()

        player1 = Player('X', ai_type=player1_type if player1_type != "human" else None)
        player2 = Player('O', ai_type=player2_type if player2_type != "human" else None)
        self.current_player = player1

        # Primera jugada automática en el centro si es IA
        center = self.board_size // 2
        if player1.ai_type:
            self.make_move(player1, center, center)
            print("Jugador 1 (IA) hizo la primera jugada en el centro.\n")

        while True:
            self.print_board()
            print(f"Turno del jugador {self.current_player.symbol}")

            if self.current_player.ai_type:
                move = self.get_ai_move(self.current_player, player2 if self.current_player == player1 else player1)
                if move:
                    row, col = move
                    print(f"IA ({self.current_player.ai_type}) elige: fila {row + 1}, columna {chr(65 + col)}")
                else:
                    print(f"No hay movimientos válidos para {self.current_player.symbol}.")
                    break
            else:
                try:
                    move = input("Ingrese su jugada (ejemplo: 8 H): ").split()
                    row = int(move[0]) - 1
                    col = ord(move[1].upper()) - 65
                except (ValueError, IndexError):
                    print("Entrada no válida. Intente nuevamente.")
                    continue

            if self.make_move(self.current_player, row, col):
                if self.check_win(self.current_player):
                    self.print_board()
                    print(f"¡Jugador {self.current_player.symbol} gana!")
                    print(f"Nodos expandidos: {self.nodes_expanded}")  # Mostrar el número de nodos expandidos
                    break
                elif self.is_full():
                    self.print_board()
                    print("¡Empate!")
                    print(f"Nodos expandidos: {self.nodes_expanded}")  # Mostrar el número de nodos expandidos
                    break
                self.current_player = player2 if self.current_player == player1 else player1
            else:
                print("Movimiento no válido. Intente nuevamente.")

    def get_ai_move(self, player, opponent):
        """
        Obtiene un movimiento basado en el tipo de IA del jugador.
        :param player: Jugador actual.
        :param opponent: Oponente.
        :return: Coordenadas del movimiento elegido (fila, columna).
        """
        if player.ai_type == "random":
            return self.random_ai()
        elif player.ai_type == "greedy":
            return self.greedy_ai(player.symbol)
        elif player.ai_type == "worst":
            return self.worst_ai(opponent.symbol)
        elif player.ai_type == "expert":
            return self.iterative_deepening(player.symbol, opponent.symbol)
        return None

    def random_ai(self):
        """
        IA que elige movimientos al azar.
        :return: Coordenadas (fila, columna) del movimiento aleatorio.
        """
        valid_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.is_valid_move(r, c)]
        return random.choice(valid_moves) if valid_moves else None

    def greedy_ai(self, symbol):
        """
        IA que elige el movimiento con mayor puntuación heurística.
        :param symbol: Símbolo del jugador actual.
        :return: Coordenadas (fila, columna) del mejor movimiento según la heurística.
        """
        best_move = None
        best_score = float('-inf')

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(row, col):
                    self.board[row][col] = symbol
                    score = self.evaluate_board(symbol)
                    self.board[row][col] = '.' 
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)

        return best_move

    def worst_ai(self, opponent_symbol):
        """
        IA que elige el peor movimiento para sí misma.
        :param opponent_symbol: Símbolo del oponente.
        :return: Coordenadas (fila, columna) del peor movimiento según la heurística.
        """
        worst_move = None
        worst_score = float('inf')

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.is_valid_move(row, col):
                    self.board[row][col] = opponent_symbol
                    score = self.evaluate_board(opponent_symbol)
                    self.board[row][col] = '.' 
                    if score < worst_score:
                        worst_score = score
                        worst_move = (row, col)

        return worst_move

    def iterative_deepening(self, symbol, opponent_symbol):
        """
        IA experta que utiliza búsqueda iterativa en profundidad (IDS) con podado alfa-beta.
        :param symbol: Símbolo del jugador actual.
        :param opponent_symbol: Símbolo del oponente.
        :return: Mejor movimiento encontrado.
        """
        start_time = time.time()
        best_move = None
        best_score = float('-inf')
        depth = 1

        while time.time() - start_time < self.ai_time_limit:
            current_best_move = None
            current_best_score = float('-inf')

            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.is_valid_move(row, col):
                        self.board[row][col] = symbol
                        score = self.minimax(depth - 1, float('-inf'), float('inf'), False, symbol, opponent_symbol, start_time)
                        self.board[row][col] = '.' 
                        if score > current_best_score:
                            current_best_score = score
                            current_best_move = (row, col)

            if current_best_move:
                best_move = current_best_move
                best_score = current_best_score
            depth += 1

        return best_move


    def minimax(self, depth, alpha, beta, maximizing_player, symbol, opponent_symbol, start_time):
        """
        Implementa el algoritmo Minimax con podado alfa-beta.
        :param depth: Profundidad actual.
        :param alpha: Mejor valor para el jugador maximizador.
        :param beta: Mejor valor para el jugador minimizador.
        :param maximizing_player: Indica si el jugador actual está maximizando.
        :param symbol: Símbolo del jugador maximizador.
        :param opponent_symbol: Símbolo del jugador minimizador.
        :param start_time: Hora de inicio para controlar el límite de tiempo.
        :return: Puntuación o movimiento en el nivel superior.
        """
        if depth == 0 or self.is_full() or time.time() - start_time > self.ai_time_limit:
            return self.evaluate_board(symbol)  # Devuelve la puntuación si se alcanza la condición terminal

        if maximizing_player:
            best_value = float('-inf')
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.is_valid_move(row, col):
                        self.board[row][col] = symbol
                        value = self.minimax(depth - 1, alpha, beta, False, symbol, opponent_symbol, start_time)
                        self.board[row][col] = '.'  
                        best_value = max(best_value, value)
                        alpha = max(alpha, value)
                        if beta <= alpha:
                            break
                        self.nodes_expanded += 1  # Contar el nodo expandido
            return best_value
        else:
            best_value = float('inf')
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.is_valid_move(row, col):
                        self.board[row][col] = opponent_symbol
                        value = self.minimax(depth - 1, alpha, beta, True, symbol, opponent_symbol, start_time)
                        self.board[row][col] = '.'  
                        best_value = min(best_value, value)
                        beta = min(beta, value)
                        if beta <= alpha:
                            break
                        self.nodes_expanded += 1  # Contar el nodo expandido
            return best_value


if __name__ == "__main__":
    game = Gomoku()
    game.play()
