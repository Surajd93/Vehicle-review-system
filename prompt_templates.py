VEHICLE_FEATURE_PROMPT = """
You are an expert automobile reviewer. Compare the two vehicles below in a structured format.

Vehicles:
1. {vehicle1}
2. {vehicle2}

Provide the comparison in EXACTLY the following 6 sections, each starting with '##':

## 1. Price & Variants
- Instead of mixing them in one table, give separate blocks like this:

### {vehicle1}
- Base Model: ₹ X,XX,XXX
- Mid Variant: ₹ X,XX,XXX
- Top Variant: ₹ X,XX,XXX

### {vehicle2}
- Base Model: ₹ X,XX,XXX
- Mid Variant: ₹ X,XX,XXX
- Top Variant: ₹ X,XX,XXX

Also include a short note about pricing trends.

## 2. Specifications Overview
Provide a side-by-side table comparing engine, mileage, weight, dimensions, fuel type, etc.

## 3. Feature Comparison
Show a table like this, use "Yes" or "No" (NOT symbols):

| Feature          | {vehicle1} | {vehicle2} |
|------------------|------------|------------|
| ABS              | Yes        | No         |
| Bluetooth        | Yes        | Yes        |

## 4. Performance Analysis
Discuss acceleration, handling, braking, comfort, mileage, long-ride suitability.

## 5. Pros & Cons
Use bullet points for Pros & Cons of both {vehicle1} and {vehicle2}.

## 6. Best Fit for Buyers
- Present this in two separate compact boxes.
- Example:

<div class="buyer-fit">
  <h4>{vehicle1}</h4>
  <p>Best for city riders, fuel efficiency, daily commuters.</p>
</div>

<div class="buyer-fit">
  <h4>{vehicle2}</h4>
  <p>Best for long rides, premium buyers, highway performance.</p>
</div>

Rules:
- Always show prices in Indian Rupees (₹) with Indian numbering format.
- Always output all 6 sections.
- Keep formatting neat and compact.
"""
