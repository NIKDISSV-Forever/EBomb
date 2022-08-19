import setuptools

with open('README.md', encoding='UTF-8') as f:
    long_description = f.read().strip()
with open('requirements.txt', encoding='UTF-8') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="EBomb",

    version="2.2.1",

    author="Nikita (NIKDISSV)",
    author_email="nikdissv@proton.me",

    description="Email Bomber",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/NIKDISSV-Forever/EBomb",
    install_requires=install_requires,
    packages=setuptools.find_packages(),

    package_dir={'EBomb': 'EBomb'},
    package_data={'EBomb': ['services.txt']},
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Typing :: Typed',
    ],

    python_requires='>=3.8',
)
