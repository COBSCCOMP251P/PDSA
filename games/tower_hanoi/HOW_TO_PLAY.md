# 🎮 How to Play Tower of Hanoi with Drag & Drop

## Quick Start Guide

### 1. Access the Game
Open your browser to: **http://localhost:3000**

### 2. Start Playing

1. **Click "Play"** in the navigation bar
2. **Fill in the form:**
   - Enter your name (e.g., "Player1")
   - Choose disk count (5-10 disks)
   - Choose peg count (3 or 4 pegs)
   - Select an algorithm (for reference/comparison)

3. **Click "Start Game"** button

### 3. Play Using Drag & Drop

Once the game loads, you'll see three or four pegs with colored disks stacked on the first peg.

#### Method 1: Drag and Drop (Recommended) 🖱️

1. **Click and hold** on the top disk of any peg
2. **Drag** it to another peg
3. **Release** to drop it
4. ✅ If valid, disk moves
5. ❌ If invalid, you'll see an error message

#### Method 2: Click to Select & Move

1. **Click** on a disk to select it (it will highlight)
2. **Click** on the destination peg
3. Disk moves if the move is valid

### 4. Game Rules

- You can only move **one disk at a time**
- You can only move the **top disk** from each peg
- A **larger disk cannot be placed on a smaller disk**
- Goal: Move all disks from the **leftmost peg** to the **rightmost peg**

### 5. Visual Feedback

- 🔵 **Blue border** = Selected disk
- 🟢 **Green highlight** = Valid drop zone while dragging
- 🔴 **Red message** = Invalid move attempt
- 👆 **Grab cursor** = Movable disk (changes to grabbing when dragging)

### 6. Win the Game

- When all disks reach the rightmost peg, you win! 🏆
- **Game saves automatically** to database
- Victory screen shows your stats
- Your move sequence is saved for analysis

### 7. Track Your Progress

While playing, watch the top section for:
- **Moves Made**: Your current move count
- **Time Elapsed**: How long you've been playing
- **Optimal Moves**: The minimum possible moves
- **Algorithm**: The algorithm selected for comparison

## 🎯 Pro Tips

1. **Smooth Dragging**: Click, hold, drag smoothly, then release
2. **Visual Cues**: Watch for green highlighting on valid pegs
3. **Cancel Move**: Drop disk back on same peg to cancel
4. **Try Both Methods**: Use drag-drop or click-select, whichever you prefer
5. **Practice**: Start with 5 disks on 3 pegs, then increase difficulty

## 🐛 Troubleshooting

### Drag not working?
- Make sure you're clicking on the **top disk** only
- Try clicking and holding for a moment before dragging
- Check browser console (F12) for any errors

### Game not showing?
- Verify frontend is running: http://localhost:3000
- Verify backend is running: http://localhost:8000
- Check browser console for errors

### Disks not visible?
- The game board appears after clicking "Start Game"
- Make sure you filled in all form fields
- Try refreshing the page

## 📊 What Happens When You Win

1. ✅ Game detects completion automatically
2. 💾 Saves to database automatically (no button needed!)
3. 🏆 Victory screen appears with stats
4. 📈 Your session is recorded with:
   - Player name
   - Move count and sequence
   - Time taken
   - Disk and peg count

## 🔄 Play Again

After winning:
- Click "New Game" to start fresh
- Click "Play Again" to retry same settings
- Or navigate back to "Play" section for new settings

## 🎨 Customization

### Difficulty Levels
- **Beginner**: 5 disks, 3 pegs (31 optimal moves)
- **Intermediate**: 7 disks, 3 pegs (127 optimal moves)
- **Advanced**: 10 disks, 3 pegs (1023 optimal moves)
- **Expert**: 10 disks, 4 pegs (much fewer moves with Frame-Stewart)

### Algorithms to Compare Against
- **Recursive 3-Peg**: Classic recursive solution
- **Iterative 3-Peg**: Stack-based solution
- **Recursive 4-Peg**: Frame-Stewart algorithm
- **Iterative 4-Peg**: Iterative Frame-Stewart

## 💡 Learning Mode

Want to see how algorithms solve it?
1. Start a game
2. Click **"Auto-Complete"** button
3. Watch the algorithm solve it
4. Click "Play Animation" to see moves animated
5. Study the move sequence to improve your strategy!

---

**Happy Playing! 🗼✨**

Need help? Check the browser console (F12) for any error messages.
