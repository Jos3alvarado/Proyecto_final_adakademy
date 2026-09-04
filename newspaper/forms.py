from django import forms
from django.contrib.auth.models import User
from .models import Article, PostType, GossipLevel, DebtStatus, LegalStatus, Category


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'post_type',
            'category',
            'title',
            'content',
            'image',
            'is_paid',
            'price',
            'is_anonymous',
            'gossip_level',
            'gossip_tags',
            'amount',
            'agreed_payment_date',
            'debtor',
            'debt_status',
            'exact_amount',
            'interest_rate',
            'due_date',
            'guarantee_document',
            'legal_status',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
            'agreed_payment_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'exact_amount': forms.NumberInput(attrs={'step': '0.01'}),
            'interest_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'gossip_tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        post_type = kwargs.pop('post_type', None)
        super().__init__(*args, **kwargs)

        if not post_type:
            if self.instance and self.instance.pk:
                post_type = self.instance.post_type
            else:
                post_type = PostType.GOSSIP

        self.post_type = post_type

        hidden_fields = [
            'is_anonymous',
            'gossip_level',
            'gossip_tags',
            'amount',
            'agreed_payment_date',
            'debtor',
            'debt_status',
            'exact_amount',
            'interest_rate',
            'due_date',
            'guarantee_document',
            'legal_status',
        ]

        for field_name in hidden_fields:
            self.fields[field_name].widget = forms.HiddenInput()
            self.fields[field_name].required = False

        if self.post_type == PostType.GOSSIP:
            self.fields['is_anonymous'].widget = forms.CheckboxInput()
            self.fields['gossip_level'].widget = forms.Select(choices=GossipLevel.choices)
            self.fields['gossip_tags'].widget = forms.SelectMultiple()
            self.fields['gossip_tags'].required = False

        elif self.post_type == PostType.PANA_DEBT:
            self.fields['amount'].widget = forms.NumberInput(attrs={'step': '0.01'})
            self.fields['amount'].required = True
            self.fields['agreed_payment_date'].widget = forms.DateInput(attrs={'type': 'date'})
            self.fields['agreed_payment_date'].required = True
            self.fields['debtor'].widget = forms.Select()
            self.fields['debtor'].required = True
            self.fields['debt_status'].widget = forms.Select(choices=DebtStatus.choices)
            self.fields['debt_status'].required = True
            self.fields['exact_amount'].widget = forms.HiddenInput()
            self.fields['interest_rate'].widget = forms.HiddenInput()
            self.fields['due_date'].widget = forms.HiddenInput()
            self.fields['guarantee_document'].widget = forms.HiddenInput()
            self.fields['legal_status'].widget = forms.HiddenInput()

        elif self.post_type == PostType.SERIOUS_DEBT:
            self.fields['exact_amount'].widget = forms.NumberInput(attrs={'step': '0.01'})
            self.fields['exact_amount'].required = True
            self.fields['interest_rate'].widget = forms.NumberInput(attrs={'step': '0.01'})
            self.fields['interest_rate'].required = True
            self.fields['due_date'].widget = forms.DateInput(attrs={'type': 'date'})
            self.fields['due_date'].required = True
            self.fields['guarantee_document'].widget = forms.FileInput()
            self.fields['legal_status'].widget = forms.Select(choices=LegalStatus.choices)
            self.fields['legal_status'].required = True
            self.fields['amount'].widget = forms.HiddenInput()
            self.fields['agreed_payment_date'].widget = forms.HiddenInput()
            self.fields['debtor'].widget = forms.HiddenInput()
            self.fields['debt_status'].widget = forms.HiddenInput()

        self.fields['category'].queryset = Category.objects.filter(post_type=self.post_type)
        self.fields['debtor'].queryset = User.objects.all()
        self.fields['price'].required = False
