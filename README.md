# AssociationRulesMiner
A tool for mining Association Rules

**This Python app will read items and transactions data from a Postgres database and write the mined rules to Neo4j**

## How to use
- Note: All the program codes are in the **src** folder
- First create a **config.yml** file with the template in the folder
- Edit the config file to connect to your database instances
- With Postgres database, you will need to:
    - Specify the table in which the data is read
    - Note: This table must have **a column associates with item id** and **a column associates with transaction id**
    - Specify the column in which the **item id** is stored
    - Specify the column in which the **transaction id** is stored
- Run the **app.py** and the rules mined will be store into your Neo4j instance
