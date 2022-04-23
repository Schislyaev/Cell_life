# Cell_life

<h1>Life and death primitive emulation</h1>

А set of cells is rendomly created with a set of parameters.
1. Gender
2. Color
3. Strength
4. Reflection

The cells moves in random directions with a random speed. The world is a torus so for a cell its infinite.

If a couple of different genders met - a new cell gets born with a color as an average of its parents. Since that they cant "date" for some time.
If a couple of the same gender meets - one wich has higher strength kills other.

In a certain time period cells can shoot. The shoot can be penetrative (red) or not (yellow). If it is - it goes from the cell shooter till its out of screen. It 
its not - it disappears when meets a cell it can kill.

If a shoot can kill a cell depends on cell Reflection parameter. If cell has it - the shoot will be reflected. Otherwise the cell will die.

<i>
The options of developing this project:<br>
1. Reshape the world to 3d.<br>
2. Invine more evolutionary sence to the cell behavour. Putting in a kind of genom which can mutate and develope through epocas.
</i>


