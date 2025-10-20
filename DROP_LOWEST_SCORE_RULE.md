# Drop Lowest Score Rule

## Overview

The BGX Racing Platform implements a **"drop lowest score"** rule for completed championships. This rule is common in motorsports and allows riders to have one bad race without it severely impacting their championship standing.

---

## 📋 Rule Definition

### **When the rule applies:**

✅ The championship status is **"completed"**  
✅ The rider participated in **ALL races** in the championship  
✅ The championship has **more than 1 race**

### **What happens:**

The rider's **lowest race score is removed** from their total championship points.

### **When the rule does NOT apply:**

❌ Championship is still "active" or "upcoming"  
❌ Rider missed one or more races  
❌ Championship has only 1 race

---

## 🎯 Example Scenario

### Championship: BGX 2024 (5 races, COMPLETED)

#### **Rider A (Participated in ALL 5 races):**

| Race | Points | Status |
|------|--------|--------|
| Sofia | 61 | ✓ |
| Plovdiv | 45 | ✓ |
| Varna | 25 | ← Lowest |
| Burgas | 50 | ✓ |
| Ruse | 40 | ✓ |

**Calculation:**
```
Raw Total:      61 + 45 + 25 + 50 + 40 = 221 points
Lowest Score:   25 points (Varna)
Final Total:    221 - 25 = 196 points ✨
```

#### **Rider B (Participated in 4 out of 5 races):**

| Race | Points | Status |
|------|--------|--------|
| Sofia | 61 | ✓ |
| Plovdiv | 45 | ✓ |
| Varna | - | ❌ Did not participate |
| Burgas | 50 | ✓ |
| Ruse | 40 | ✓ |

**Calculation:**
```
Raw Total:      61 + 45 + 0 + 50 + 40 = 196 points
Lowest Score:   NOT DROPPED (didn't participate in all races)
Final Total:    196 points
```

**Result:** Both riders have 196 points, but Rider A benefited from the drop rule!

---

## 💻 Technical Implementation

### **Backend (Django)**

**File:** `bgx-api/results/calculations.py`

```python
def calculate_championship_results(championship):
    """
    Calculate championship standings from race results
    
    Special rule: If championship is completed and rider participated in ALL races,
    drop their lowest race score from the total.
    """
    
    total_races_in_championship = races.count()
    is_championship_completed = championship.status == 'completed'
    
    for category in categories:
        category_results = race_results.filter(category=category)
        races_participated = category_results.count()
        
        # Calculate total points
        total_points = sum(result.total_points for result in category_results)
        
        # Apply drop-lowest-score rule
        dropped_points = Decimal(0)
        if is_championship_completed and races_participated == total_races_in_championship:
            if races_participated > 1:
                points_list = [result.total_points for result in category_results]
                lowest_score = min(points_list)
                total_points -= lowest_score
                dropped_points = lowest_score
        
        ChampionshipResult.objects.update_or_create(
            championship=championship,
            rider=rider,
            category=category,
            defaults={
                'total_points': total_points,
                'races_participated': races_participated,
                'lowest_score_dropped': dropped_points,
            }
        )
```

### **Database Model**

**File:** `bgx-api/results/models.py`

```python
class ChampionshipResult(models.Model):
    championship = models.ForeignKey('championships.Championship', ...)
    rider = models.ForeignKey('riders.Rider', ...)
    category = models.CharField(max_length=20)
    
    total_points = models.DecimalField(...)  # After dropping lowest
    races_participated = models.IntegerField(...)
    lowest_score_dropped = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Lowest race score dropped (if applicable)"
    )
```

### **API Response**

**Endpoint:** `GET /api/results/championship-results/?championship=1&category=profi`

**Response:**
```json
[
  {
    "id": 1,
    "championship": 1,
    "championship_name": "BGX Championship 2024",
    "championship_status": "completed",
    "rider": 5,
    "rider_name": "John Doe",
    "rider_club": "Racing Club Sofia",
    "category": "profi",
    "total_points": 196,
    "races_participated": 5,
    "lowest_score_dropped": 25
  }
]
```

### **Frontend Display**

**File:** `bgx-fe/src/components/ChampionshipResults.jsx`

The frontend displays:
- **Info banner** when viewing completed championship standings
- **Dropped score** below the total points (if applicable)

```jsx
{result.lowest_score_dropped > 0 && (
  <span className="text-xs text-gray-500">
    (Dropped: {result.lowest_score_dropped} pts)
  </span>
)}
```

---

## 🔄 Automatic Recalculation

The rule is **automatically applied** when:

1. **Race results are entered** → Championship results recalculated
2. **Championship status changes to "completed"** → Results recalculated
3. **Admin triggers manual recalculation** → All results updated

**Signal Handler:** `bgx-api/results/signals.py`

```python
@receiver(post_save, sender=RaceDayResult)
def recalculate_on_result_save(sender, instance, created, **kwargs):
    race = instance.race_day.race
    recalculate_all(race=race)  # ✨ Automatically updates championship results
```

---

## 🎨 User Interface

### **Championship Results Page**

When viewing a **completed championship**:

1. **Blue info banner** appears:
   ```
   ℹ️ Completed championship: Riders who participated in all races 
      have their lowest score dropped
   ```

2. **Points display** shows:
   ```
   196 pts
   (Dropped: 25 pts)
   ```

3. **Translation support:**
   - **English:** "Dropped: 25 pts"
   - **Bulgarian:** "Премахнато: 25 pts"

---

## 🧪 Testing the Rule

### **Setup:**

1. Create a championship with 3+ races
2. Add riders with race day results
3. Ensure at least one rider participates in ALL races
4. Mark the championship as **"completed"**

### **Expected Behavior:**

```python
# Rider A (all 3 races): 50, 30, 45 points
# Expected: 50 + 45 = 95 points (dropped 30)

# Rider B (2 out of 3 races): 50, 45 points  
# Expected: 50 + 45 = 95 points (no drop, missed a race)
```

### **Verify:**

```bash
# Run manual recalculation
make shell
python manage.py shell

from championships.models import Championship
from results.calculations import recalculate_all

champ = Championship.objects.get(id=1)
champ.status = 'completed'
champ.save()

recalculate_all(championship=champ)

# Check results
from results.models import ChampionshipResult
ChampionshipResult.objects.filter(championship=champ).values(
    'rider__first_name', 
    'total_points', 
    'races_participated', 
    'lowest_score_dropped'
)
```

---

## 📊 Database Migration

### **Required Migration:**

```bash
# Create migration for new field
make makemigrations

# Apply migration
make migrate
```

**Migration adds:**
- `lowest_score_dropped` field to `ChampionshipResult` model (default: 0)

---

## 🔍 Admin Interface

The Django admin shows:

1. **ChampionshipResult list:**
   - Total points (after drop)
   - Races participated
   - Lowest score dropped

2. **Championship status:**
   - Can be changed to "completed" to trigger rule
   - Manual recalculation available via admin action

---

## 🚨 Important Notes

### **Fairness:**

- Only riders who **committed to all races** get this benefit
- Encourages full championship participation
- Common rule in F1, MotoGP, and other motorsports

### **Transparency:**

- Dropped score is **stored and displayed**
- Users can see exactly which score was dropped
- Total transparency in calculations

### **Performance:**

- Calculations are **automatic** via Django signals
- No manual intervention needed
- Cached in database for fast queries

---

## 📚 Related Files

### **Backend:**
- `bgx-api/results/models.py` - Database models
- `bgx-api/results/calculations.py` - Calculation logic
- `bgx-api/results/serializers.py` - API serializers
- `bgx-api/results/signals.py` - Auto-recalculation

### **Frontend:**
- `bgx-fe/src/components/ChampionshipResults.jsx` - Results display
- `bgx-fe/src/i18n/locales/en.json` - English translations
- `bgx-fe/src/i18n/locales/bg.json` - Bulgarian translations

---

## 🎯 Summary

✅ **Automatic:** Rule applies when championship is completed  
✅ **Fair:** Only for riders who participated in all races  
✅ **Transparent:** Dropped score is shown to users  
✅ **Multilingual:** Fully translated (EN/BG)  
✅ **Tested:** Automatic recalculation via signals  

The drop lowest score rule is now fully implemented and will automatically apply to completed championships! 🏆

