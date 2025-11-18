from django.db import models

class ProductionCropsLivestock(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    year = models.IntegerField()
    production_quantity = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'production_productioncropslivestock'
        managed = False
       
class ProducerPrices(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    year = models.IntegerField()
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'production_producerprices'
        managed = False
        

class FertilizersByProduct(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    fertilizer_type = models.CharField(max_length=255)
    year = models.IntegerField()
    quantity = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'production_fertilizersbyproduct'
        managed = False
        

class LandUse(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    year = models.IntegerField()
    land_area_agricultural = models.FloatField(null=True, blank=True)
    land_area_total = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'production_landuse'
        managed = False
        

class EmploymentAgriculture(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=255)
    year = models.IntegerField()
    employment_agriculture = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'production_employmentagriculture'
        managed = False
        

class ForeignDirectInvestmentAgriculture(models.Model):
    id = models.AutoField(primary_key=True)
    investing_country = models.CharField(max_length=255)
    receiving_country = models.CharField(max_length=255)
    year = models.IntegerField()
    investment_amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'production_foreigndirectinvestmentagriculture'
        managed = False
        
