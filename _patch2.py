import re

path = 'c:/Users/Quentin/Documents/GitHub/quentinwalkingtour/index.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'⛪ <strong>Notre-Dame Cathedral</strong>.*?🥐 Small cafés, local spots &amp; authentic Parisian life\.'

replacement = '''⚔️ <strong>Cannonball and bullet marks</strong> are still visible on some walls, silent witnesses to <strong>revolutions and wars</strong> that shaped Paris and world history.<br /><br />
👑 Meet the people who made Paris what it is today: <strong>women in the Resistance</strong>, <strong>Victor Hugo</strong>, republican revolutionaries, kings, emperors… and <strong>Emmanuel Macron</strong>!<br /><br />
🌆 From the <strong>fire of Notre-Dame</strong> to protests in the streets, we explore how <strong>recent events influenced everyday life</strong> in Paris. This is history still alive today.<br /><br />
🏰 Turning a corner, you might suddenly find yourself facing <strong>medieval houses</strong> (somehow still standing 😂), or the remains of <strong>fortification walls</strong> hidden within the modern city.<br /><br />
🥐 <strong>Le Marais</strong> is the beating heart of Paris, where <strong>fashion, small cafés, restaurants, and local life</strong> all mix together in one vibrant district.'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
if new_content != content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS')
else:
    # Try without HTML entity
    pattern2 = r'⛪ <strong>Notre-Dame Cathedral</strong>.*?🥐 Small cafés, local spots & authentic Parisian life\.'
    new_content2 = re.sub(pattern2, replacement, content, flags=re.DOTALL)
    if new_content2 != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content2)
        print('SUCCESS (variant)')
    else:
        idx = content.find('Notre-Dame Cathedral')
        print('NOT MATCHED. Context:')
        print(repr(content[idx-50:idx+400]))
