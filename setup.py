import setuptools

with open('README.md', encoding='UTF-8') as f:
    long_description = f.read()
with open('requires.txt', encoding='UTF-8') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="EBomb",

    version="1.0.0",

    author="Nikita (NIKDISSV)",
    author_email="nikdissv.forever@protonmail.com",

    description="proxytv.ru IPTV Channels Parser and Robot",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/NIKDISSV-Forever/ProxyTVRobot",
    install_requires=install_requires,
    packages=setuptools.find_packages(),

    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Typing :: Typed',
    ],

    python_requires='>=3.6',
)
