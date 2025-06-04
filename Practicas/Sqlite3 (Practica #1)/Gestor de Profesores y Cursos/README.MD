## Diagrama Entidad-Relación

```markdown
+-------------------+
| Profesores        |
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
