# Avatar Configuration

This file controls the AI avatars in the Agora Chat application.

## Avatar Settings

### Neura
- **Active**: true
- **Name**: Neura
- **Prompt File**: prompts/kora_prompt.md
- **Color**: from-purple-500 to-blue-500
- **Text Color**: text-purple-300
- **Icon**: fas fa-leaf
- **Allow Follow-ups**: false
- **Speaker Order**: 1

### Lucy
- **Active**: true
- **Name**: Lucy
- **Prompt File**: prompts/sassi_prompt.md
- **Color**: from-pink-500 to-rose-500
- **Text Color**: text-pink-300
- **Icon**: fas fa-palette
- **Allow Follow-ups**: false
- **Speaker Order**: 2

### Riku
- **Active**: false
- **Name**: Riku
- **Prompt File**: prompts/riku_prompt.md
- **Color**: from-green-500 to-emerald-500
- **Text Color**: text-green-300
- **Icon**: fas fa-brain
- **Allow Follow-ups**: false
- **Speaker Order**: 3

## Configuration Notes

- **Active**: Set to `false` to disable an avatar completely
- **Name**: Display name for the avatar (can be changed)
- **Prompt File**: Path to the avatar's personality prompt file
- **Color**: Tailwind CSS gradient classes for avatar background
- **Text Color**: Tailwind CSS text color class for avatar name
- **Icon**: Font Awesome icon class for avatar
- **Allow Follow-ups**: Set to `false` to prevent this avatar from giving @mention follow-up responses
- **Speaker Order**: Numeric order for avatar responses (1 = first, 2 = second, etc.)

## Examples

To disable Riku:
```
### Riku
- **Active**: false
```

To rename Sassi to "Sophie":
```
### Sassi
- **Name**: Sophie
```

To prevent Kora from giving follow-ups:
```
### Kora
- **Allow Follow-ups**: false
```

To make Lucy speak first:
```
### Lucy
- **Speaker Order**: 1
```