# Command Hierarchy Documentation - Quick Guide

## Generated Files

All files are located in `docs/`:

### 1. **command-hierarchy-split.md** ⭐ RECOMMENDED (9KB, 246 lines)
- **Multiple small, readable diagrams**
- One diagram per context
- Left-to-right layout for each context
- **Most readable option!**

### 2. **command-hierarchy-lr.md** (9KB, 324 lines)
- **Single left-to-right diagram**
- Flows left to right instead of top-down
- Better horizontal space usage

### 3. **command-hierarchy-flow.md** (2KB, 50 lines)
- **Simplified context navigation map**
- Shows only how to navigate between contexts
- Great for understanding the "big picture"

### 4. **command-hierarchy.md** (16KB, 470 lines)
- **Full comprehensive single diagram**
- Contains everything in one view
- Can be overwhelming but complete

## 📖 How to Choose

| Use Case | Recommended File | Why |
|----------|------------------|-----|
| **Best readability** | `command-hierarchy-split.md` | Small, focused diagrams |
| **Context navigation** | `command-hierarchy-flow.md` | Shows flow between contexts |
| **Horizontal layout** | `command-hierarchy-lr.md` | Fits wide screens better |
| **Complete view** | `command-hierarchy.md` | Everything in one place |

## 🔍 Quick Comparison

### Split Format (Recommended)
```
Diagram 1: Context Overview
Diagram 2: VPC Context (left-to-right)
Diagram 3: Transit Gateway Context (left-to-right)
...
```

### Left-to-Right Format
```
aws-net → set vpc → vpc → show detail → show subnets
```

### Flow Format (Simple)
```
root --set vpc--> vpc
vpc --set route-table--> route-table
```

## 🚀 Opening with Typora

```bash
# RECOMMENDED: Most readable
typora docs/command-hierarchy-split.md

# Simple navigation flow
typora docs/command-hierarchy-flow.md

# Horizontal layout
typora docs/command-hierarchy-lr.md

# Full comprehensive view
typora docs/command-hierarchy.md
```

## 📊 File Sizes

- `command-hierarchy-split.md`: 9.8KB, 246 lines ⭐
- `command-hierarchy-lr.md`: 9.5KB, 324 lines
- `command-hierarchy-flow.md`: 1.7KB, 50 lines
- `command-hierarchy.md`: 15.9KB, 470 lines

## ✅ All Formats Include

- Entity Relationship Diagrams (Mermaid)
- Command listings by context
- Implementation status (✓/○)
- Navigation paths
- Complete command paths
- Statistics

Start with `command-hierarchy-split.md` for the best reading experience!
