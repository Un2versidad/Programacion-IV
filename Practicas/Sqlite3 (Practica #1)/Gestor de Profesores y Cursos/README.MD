## Diagrama Entidad-Relación

```markdown
+-------------------+
| Profesore         |
|-------------------|
| PK id             | <---+
|    nombre         |     |
|    especialidad   |     | 
+-------------------+-----+
                          |
+-------------------+     |
| Cursos            |     |
|-------------------|     |
| PK id             |     |
|    titulo         |     |
| FK id-profesor ---+-----+ 
+-------------------+
```
