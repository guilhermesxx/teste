from rest_framework import serializers
from .models import Usuario, Livro, Emprestimo

# --------------------------
# SERIALIZER DE USUÁRIO
# --------------------------
class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'ra', 'nome', 'email', 'turma', 'tipo', 'senha']
        extra_kwargs = {
            'senha': {'write_only': True},
        }

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        user = Usuario.objects.create_user(**validated_data, senha=senha)
        return user

    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            instance.set_password(validated_data.pop('senha'))
        return super().update(instance, validated_data)

# --------------------------
# SERIALIZER DE LIVRO
# --------------------------
class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'data_publicacao', 'tipo', 'disponivel']

# --------------------------
# SERIALIZER DE EMPRÉSTIMO
# --------------------------
class EmprestimoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    livro = LivroSerializer(read_only=True)
    livro_id = serializers.PrimaryKeyRelatedField(
        queryset=Livro.objects.all(), source='livro', write_only=True
    )

    class Meta:
        model = Emprestimo
        fields = ['id', 'usuario', 'livro', 'livro_id', 'data_emprestimo', 'data_devolucao', 'devolvido']
        read_only_fields = ['data_emprestimo', 'data_devolucao', 'devolvido']

    def create(self, validated_data):
        # A validação será feita pelo model via clean()
        return Emprestimo.objects.create(**validated_data)
