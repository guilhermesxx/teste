from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError

# -----------------------------
# GERENCIADOR DE USUÁRIO
# -----------------------------
class UsuarioManager(BaseUserManager):
    def create_user(self, ra, nome, email, senha=None, tipo='aluno', turma=None):
        if not email:
            raise ValueError('Usuários devem ter um e-mail')

        if tipo == 'aluno' and not turma:
            raise ValueError('Alunos devem ter uma turma')

        user = self.model(
            ra=ra,
            nome=nome,
            email=self.normalize_email(email),
            tipo=tipo,
            turma=turma
        )
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, ra, nome, email, turma=None, tipo='admin', senha=None):
        user = self.create_user(
            ra=ra,
            nome=nome,
            email=email,
            turma=turma,
            tipo=tipo,
            senha=senha
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# -----------------------------
# MODELO DE USUÁRIO
# -----------------------------
class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('admin', 'Administrador'),
    ]

    ra = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    turma = models.CharField(max_length=10, null=True, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['ra', 'nome', 'tipo']

    def __str__(self):
        return self.nome

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome


# -----------------------------
# MODELO DE LIVRO
# -----------------------------
class Livro(models.Model):
    TIPO_CHOICES = [
        ('fisico', 'Físico'),
        ('digital', 'Digital'),
    ]

    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    data_publicacao = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo']


# -----------------------------
# MODELO DE EMPRÉSTIMO
# -----------------------------
class Emprestimo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    devolvido = models.BooleanField(default=False)

    def clean(self):
        if not self.livro.disponivel:
            raise ValidationError("Este livro não está disponível para empréstimo.")

    def marcar_devolucao(self):
        if not self.devolvido:
            self.data_devolucao = timezone.now()
            self.devolvido = True
            self.livro.disponivel = True
            self.livro.save()
            self.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # chama o clean() e valida regras
        if not self.pk:  # novo empréstimo
            self.livro.disponivel = False
            self.livro.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.usuario.nome} - {self.livro.titulo}'
