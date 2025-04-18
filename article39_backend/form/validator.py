from django.core.exceptions import ValidationError

def validate_budget_breakdown(budget_breakdown):
    if not isinstance(budget_breakdown, dict):
        raise ValidationError("Budget breakdown must be a dictionary.")

    pre_production = budget_breakdown.get('pre_production', {})
    validate_cost_section(pre_production, ['script_writing', 'storyboarding_concept_art', 'location_scouting', 'administrative'])

    talent_and_crews = budget_breakdown.get('talent_and_crews', {})
    validate_artists_or_crews(talent_and_crews, 'artists', 'artist_subtotal_cost')
    validate_artists_or_crews(talent_and_crews, 'crews', 'crew_subtotal')
    validate_number_field(talent_and_crews, 'overall_crew_subtotal')

    equipment_and_technical = budget_breakdown.get('equipment_and_technical', {})
    validate_equipment_section(equipment_and_technical, 'cameras', 'camera_subtotal')
    validate_cost_section(equipment_and_technical, ['lighting_equipment', 'sound_recording_equipment', 'others'])

    location_and_sets = budget_breakdown.get('location_and_sets', {})
    validate_cost_section(location_and_sets, ['location_rent', 'set_construct', 'production_design'])

    transportation_and_logistics = budget_breakdown.get('transportation_and_logistics', {})
    validate_cost_section(transportation_and_logistics, ['vehicle_rent', 'fuel', 'driver_fee'])

    wardrobe_and_costumes = budget_breakdown.get('wardrobe_and_costumes', {})
    validate_cost_section(wardrobe_and_costumes, ['costume_purchase', 'styling'])

    catering = budget_breakdown.get('catering', {})
    validate_number_field(catering, 'num_of_days')
    validate_number_field(catering, 'per_day')
    validate_number_field(catering, 'subtotal')

    snacks_craft_services = budget_breakdown.get('snacks_craft_services', {})
    validate_number_field(snacks_craft_services, 'fee')

    post_production = budget_breakdown.get('post_production', {})
    validate_cost_section(post_production, ['editing', 'color_grading', 'sound_design', 'music', 'additional'])

    contingency_misc = budget_breakdown.get('contingency_misc', {})
    validate_cost_section(contingency_misc, ['contingency_fund', 'insurance'])

def validate_number_field(section, field):
    value = section.get(field)
    if not isinstance(value, (int, float)):
        raise ValidationError(f"'{field}' must be a number.")

def validate_cost_section(section, fields):
    for field in fields:
        validate_number_field(section, field)

def validate_artists_or_crews(section, key, subtotal_field):
    items = section.get(key, [])
    if not isinstance(items, list):
        raise ValidationError(f"'{key}' must be a list.")
    
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError(f"Each item in '{key}' must be a dictionary.")

        required_fields = ['name', 'phone', 'photo', 'role', 'rate', 'num_of_days', 'total_cost']
        for field in required_fields:
            if field not in item:
                raise ValidationError(f"Each item in '{key}' must include '{field}'.")
            if field in ['rate', 'num_of_days', 'total_cost']:
                validate_number_field(item, field)
    
    validate_number_field(section, subtotal_field)

def validate_equipment_section(section, key, subtotal_field):
    items = section.get(key, [])
    if not isinstance(items, list):
        raise ValidationError(f"'{key}' must be a list.")
    
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError(f"Each item in '{key}' must be a dictionary.")

        required_fields = ['name', 'type', 'rate']
        for field in required_fields:
            if field not in item:
                raise ValidationError(f"Each item in '{key}' must include '{field}'.")
            if field == 'rate':
                validate_number_field(item, field)
    
    validate_number_field(section, subtotal_field)