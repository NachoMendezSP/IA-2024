import itertools
import random


class Minesweeper():
    """Minesweeper game representation"""

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """Prints a text-based representation of where mines are located."""

        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """Checks if all mines have been flagged."""

        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """Returns the set of all cells in self.cells known to be mines."""

        if self.count == len(self.cells):
            return self.cells
        return None

    def known_safes(self):
        """Returns the set of all cells in self.cells known to be safe."""

        if not self.count:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """Minesweeper game player"""

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
            based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
            if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
            if they can be inferred from existing knowledge
        """

        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe, updating all knowledge
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base
        #    It will describe the nearby cells and how many are mines.
        cells = set()

        # Loop over all cells within one row and column of the current cell
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Add unexplored cells to the sentence
                if 0 <= i < self.height and 0 <= j < self.width:
                    # If the cell has not been clicked or marked as a mine
                    if (i, j) not in self.moves_made and (i, j) not in self.mines:
                        cells.add((i, j))
                    # If the cell is already a known mine, decrease the count of remaining mines
                    elif (i, j) in self.mines:
                        count -= 1

        # Add the new sentence to knowledge base (describes the cells and the remaining mine count)
        self.knowledge.append(Sentence(cells, count))

        # 4) Mark any additional cells as safe or mines based on the updated knowledge base
        #    This will help deduce more information from the newly added sentence.
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            if safes:
                for safe in safes.copy():
                    self.mark_safe(safe)  # Mark known safe cells

            mines = sentence.known_mines()
            if mines:
                for mine in mines.copy():
                    self.mark_mine(mine)  # Mark known mines

        # 5) Infer any new sentences by comparing existing knowledge
        #    We create new knowledge by comparing two sentences: if one is a subset of another,
        #    we can infer a new sentence based on the difference between the two.
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 is sentence2:
                    continue
                if sentence1 == sentence2:
                    # If both sentences are the same, remove the duplicate sentence
                    self.knowledge.remove(sentence2)
                elif sentence1.cells.issubset(sentence2.cells):
                    # If sentence1 is a subset of sentence2, deduce new knowledge
                    new_sentence = Sentence(
                        sentence2.cells - sentence1.cells,
                        sentence2.count - sentence1.count
                    )
                    # Add the new knowledge if it's not already known
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                        
        # Example: if we know that {(2, 4), (3, 2), (4, 2)} = 1
        #                      and {(2, 4), (3, 2)} = 1
        #                      we get {(4, 2)} = 0 by substracting the subsets and counts
        #                      so we can deduce that (4, 2) is safe 
        #                      because the mine must be in either (2, 4) or (3, 2).


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        available_moves = self.safes - self.moves_made
        if available_moves:
            return random.choice(tuple(available_moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # If no move can be made, return None
        if len(self.mines) + len(self.moves_made) == self.height * self.width:
            return None

        # We create a list of all potential moves that haven't been made and aren't mines
        possible_moves = [
            (i, j) for i in range(self.height) for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]

        # If there are any possible moves, return one at random, otherwise return None
        return random.choice(possible_moves) if possible_moves else None