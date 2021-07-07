### Projects:

## COVID themed graph traversal
## Naive Bayes IMDB review scraper

### Requirements

python==3.8.10

numpy==1.20.3

### How to Use 

1. Install Python and libraries

2. Change working directory to project directory

3. Type "python driver.py"

### Running the program 

1. First the user creates a grid by entering an integer for both
   the number of rows and number of columns.

2. After the grid is displayed, the user may then select a type
   for various tiles in the grid, by first entering the tile 
   number and then the type: Q for Quarantine, P for PlayGround,
   or V for Vaccine. When done, the user simply enters ## twice.

3. User then enters the x and y coordinates of the START point, 
   followed by the x and y coordinates of the END point.

4. Finally, the user enters either C, V or P depending on the 
   role it wants to play. 

5. Depending on which role was selected, the corresponding 
   A*-algorithm will be called upon, and the shortest path 
   (if any) will be displayed, along with its cost. 
