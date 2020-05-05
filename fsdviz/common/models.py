"""
This file contains all of the django orm models for entities that will
be shared across both the stocking and cwt recovery applications.

"""

from django.contrib.gis.db import models
from django.template.defaultfilters import slugify


class BuildDate(models.Model):
    """
    A database to hold the date that the database was last refreshed.
    """

    build_date = models.DateField(editable=False)

    def __str__(self):
        return self.build_date.strftime("%d-%b-%Y")


class Readme(models.Model):
    """
    a table to hold all of the information regarding last FSIS
    download and FS_Master rebuild (it appear as a footer on every
    page)
    """

    date = models.DateField(editable=False)
    comment = models.TextField()
    initials = models.CharField(max_length=4)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.comment


class Agency(models.Model):
    """
    A lookup table for agencies that either stock fish or recovery cwts.

    This table should probably be extended to include office/hatchery
    so that we can differentiate offices for agencies that have more
    than one. Keeping it simple for now.

    """

    abbrev = models.CharField(max_length=15, unique=True)
    agency_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Agencies"
        ordering = ["abbrev"]

    def get_by_natural_key(self, abbrev):
        """a helper method that will allow us to get agencies
        using abbrev as the key."""
        return self.get(abbrev=abbrev)

    def __str__(self):
        """ String representation for a agency."""
        return "{} ({})".format(self.agency_name, self.abbrev)


class Lake(models.Model):
    """
    A lookup table for lakes where fish were stocked, cwts either
    deployed or recovered, or where management/spatial units are located.

    """

    abbrev = models.CharField(max_length=2, unique=True)
    lake_name = models.CharField(max_length=30, unique=True)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)

    # geom including associated watersheds
    # geom_plus = models.MultiPolygonField(srid=4326, blank=True, null=True)

    class Meta:
        ordering = ["abbrev"]

    def __str__(self):
        """ String representation for a lake."""
        return "{} ({})".format(self.lake_name, self.abbrev)

    def short_name(self):
        """The name of the lake without 'Lake ..'.

        A shorter verson of the lake name to save spave when
        needed. THis may need to be turned into a property at some
        point.

        """

        return self.lake_name.replace("Lake ", "")


class StateProvince(models.Model):
    """
    A lookup table for states or provinces where fish were stocked,
    cwts either deployed or recovered, or where management/spatial
    units are located.

    """

    COUNTRIES = (("USA", "U.S.A."), ("CAN", "Canada"))

    abbrev = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=300)
    country = models.CharField(max_length=3, choices=COUNTRIES)

    class Meta:
        ordering = ["abbrev"]

    def __str__(self):
        """ String representation for a State."""
        return "{} ({})".format(self.name, self.abbrev)


class Jurisdiction(models.Model):
    """A lookup table for geographic extents of a state or province
    within a lake.  This will be important for managers to find the
    waters that they are responsible for.

    For many states, there will only be a single juristiction
    (e.g. the Illinois waters of Lake Michigan), Michigan and Ontaio
    will have multiple juristictions (one for each lake they have in
    their pervue(??))

    A geom will be used to capture the outline of the juristiction
    within the great lake shoreline, but extends will be updated to
    include stocking events in tributatries so that map widgets can be
    appropriately zoomed so that events aren't clipped.

    """

    lake = models.ForeignKey(Lake, default=1, on_delete=models.CASCADE)
    stateprov = models.ForeignKey(StateProvince, default=1, on_delete=models.CASCADE)

    slug = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=300)

    # complete geometry of shoreline and state/province boundaries
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)
    # juristiction including associated watersheds
    # geom_plus = models.MultiPolygonField(srid=4326, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        """ String representation for a State."""
        return "{} - {} waters".format(self.lake.lake_name, self.stateprov.name)

    def save(self, *args, **kwargs):
        """
        Populate slug when we save the object.
        """
        # if not self.slug:
        self.slug = slugify("_".join([self.lake.abbrev, self.stateprov.abbrev]))

        super(Jurisdiction, self).save(*args, **kwargs)

    @property
    def centroid():
        """Return the centroid for this grid - used by the serializer.
        """
        if self.geom:
            return self.geom.centroid
        else:
            return None


class ManagementUnit(models.Model):
    """
    a class to hold geometries associated with arbirary ManagementUnits
    that can be represented as polygons.  Examples include quota
    management units and lake trout rehabilitation zones.  Used to find
    stocking events, cwts, and cwt recoveries occurred in (or
    potentially near) specific management Units.

    """

    label = models.CharField(max_length=25)
    slug = models.SlugField(blank=True, unique=True, editable=False)
    description = models.CharField(max_length=300)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)
    # geom including associated watersheds
    # geom_plus = models.MultiPolygonField(srid=4326, blank=True, null=True)

    # centroid = models.PointField(srid=4326, blank=True, null=True)
    lake = models.ForeignKey(Lake, default=1, on_delete=models.CASCADE)

    primary = models.BooleanField(
        "Primary management unit type for this jurisdiciton.",
        default=False,
        db_index=True,
    )

    MU_TYPE_CHOICES = (
        ("mu", "Management Unit"),
        ("ltrz", "Lake Trout Rehabilitation Zone"),
        ("qma", "Quota Management Area"),
        ("aa", "Assessment Area"),
        ("stat_dist", "Statistical District"),
    )

    mu_type = models.CharField(max_length=10, choices=MU_TYPE_CHOICES, default="mu")

    grid10s = models.ManyToManyField("Grid10")

    class Meta:
        ordering = ["lake__abbrev", "mu_type", "label"]

    def get_slug(self):
        """
        the name is a concatenation of lake abbreviation, the managemnet unit
        type and and the management unit label.
        """

        lake = str(self.lake.abbrev)

        return slugify("_".join([lake, self.mu_type, self.label]))

    def name(self):
        """
        returns the name of the managment unit including the lake it
        is associated with, the management unit type and the label

        """
        return " ".join([str(self.lake), self.mu_type.upper(), self.label])

    def __str__(self):
        return self.name()

    def save(self, *args, **kwargs):
        """
        Populate slug when we save the object.
        """
        # if not self.slug:
        self.slug = self.get_slug()
        super(ManagementUnit, self).save(*args, **kwargs)


class Grid10(models.Model):
    """'
    A lookup table for 10-minute grids within lakes.  Used to verify
    stocking and recovery data before being inserted.

    """

    lake = models.ForeignKey(Lake, default=1, on_delete=models.CASCADE)
    grid = models.CharField(max_length=4)
    slug = models.SlugField(blank=False, unique=True, editable=False)
    geom = models.MultiPolygonField(srid=4326, blank=True, null=True)
    centroid = models.PointField(srid=4326, blank=True, null=True)

    class Meta:
        ordering = ["lake__abbrev", "grid"]

    def __str__(self):
        """ String representation for a State."""
        return "{} ({})".format(self.grid, self.lake.abbrev)

    def get_slug(self):
        """
        the name is a concatenation of lake abbreviation, the managemnet unit
        type and and the management unit label.
        """
        lake = str(self.lake.abbrev)

        return slugify("_".join([lake, self.grid]))

    def save(self, *args, **kwargs):
        """Populate slug and centroid when we save the object.  Grid10
        centroids are used in dynamic maps so it makes sense to
        pre-caclulate them when they are created or updated.
        """
        # update out centroid if there is a geom
        if self.geom:
            self.centroid = self.geom.centroid

        # if not self.slug:
        self.slug = self.get_slug()
        super(Grid10, self).save(*args, **kwargs)


class Species(models.Model):
    """
    A lookup table for species.  Note that both backcross and splake
    are considered species and not lake trout strains.

    """

    abbrev = models.CharField(max_length=5, unique=True)
    common_name = models.CharField(max_length=50, unique=True)
    speciescommon = models.CharField(max_length=50, unique=True, blank=True, null=True)
    scientific_name = models.CharField(max_length=50, blank=True, null=True)
    # family = models.CharField(max_length=50)
    species_code = models.IntegerField(unique=True)

    strains = models.ManyToManyField(
        "Strain", through="StrainRaw", related_name="species"
    )

    class Meta:
        verbose_name_plural = "Species"
        ordering = ["abbrev"]

    def __str__(self):
        """ String representation for a Species."""
        return "{} ({})".format(self.common_name.title(), self.abbrev)


class Strain(models.Model):
    """
    This table contains the 'nominal' names for each strain.  Allows
    "SEN(86)", "SEN(87)", "SEN(88)", "SEN(89)", "SEND", "SN", "SNHW",
    "SNNM", "SLD", "SLDSLW", "SLW" to all be referred to as Seneca (SN)
    lake trout.

    TODO: create a slug field that uses the species abbrev and the strain code:

    "{}-{}".format( x.strain_code, x.strain_species.abbrev)

    """

    strain_code = models.CharField(max_length=10)
    strain_label = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)

    strain_species = models.ForeignKey("Species", on_delete=models.CASCADE)

    slug = models.CharField(max_length=20, unique=True, null=True)

    class Meta:
        ordering = ["species__abbrev", "strain_code"]
        unique_together = ("strain_species", "strain_code")

    def save(self, *args, **kwargs):
        """
        Populate slug when we save the object.
        """
        # if not self.slug:
        self.slug = slugify(
            "{}-{}".format(self.strain_species.abbrev, self.strain_code)
        )
        super(Strain, self).save(*args, **kwargs)

    def __str__(self):
        species_name = self.strain_species.common_name.title()
        return "{} Strain {} ({})".format(
            self.strain_label, species_name, self.strain_code
        )


class StrainRaw(models.Model):
    """
    The raw strain codes will represent the information returned in the
    GLFC look-up table where strain has too much information - eg -
    origins and rearing hatchery.  Essentially, this is an association
    table between the :model:`common.Species` and
    the :model:`common.Strain` tables. This table is rarely used
    directly. Generally :model:`common.Strain` is the table you want.

    """

    species = models.ForeignKey(
        Species, on_delete=models.CASCADE, related_name="rawstrain"
    )
    strain = models.ForeignKey(
        Strain, on_delete=models.CASCADE, related_name="rawstrain"
    )

    # raw_strain_code = models.CharField(max_length=10)
    raw_strain = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    class Meta:
        ordering = ["species__abbrev", "raw_strain"]
        unique_together = ("species", "strain", "raw_strain")

    def __str__(self):
        return "{} ({})".format(self.description, self.raw_strain)


class Mark(models.Model):
    """
    Stores a single mark applied to fish when they are stocked and
    reported when they are recaptured.  Includes fin clips, the
    presence of a cwt, and chemical marks.  Multiple marks can
    be applied to a single fish.  Combinations of marks most often
    serve to indicate year-class.
    """

    MARK_TYPE_CHOICES = [
        ("chemical", "Chemical"),
        ("finclip", "Fin Clip"),
        ("tag", "Tag"),
        ("unknown", "Unknown"),
    ]

    clip_code = models.CharField(max_length=2)
    mark_code = models.CharField(max_length=4, unique=True)
    mark_type = models.CharField(
        max_length=8, choices=MARK_TYPE_CHOICES, default="finclip"
    )

    description = models.CharField(max_length=100)

    class Meta:
        ordering = ["mark_type", "mark_code"]

    def __str__(self):
        return "{} ({})".format(self.description, self.mark_code)


class LatLonFlag(models.Model):
    """
    Inicates the level of spatial precision associated with a stocking
    event or recovery effort.  Lower numbers indicate higher precision.

    """

    value = models.IntegerField(unique=True)
    description = models.CharField(max_length=100)

    class Meta:
        ordering = ["value"]

    def __str__(self):
        return "{} - {}".format(self.value, self.description)


class CWT(models.Model):
    """
    A model representing a single CWT object.  CWT has a foreign key back to
    :model:`common.Agency` and current a single cwt_number and cwt manufacturer
    must be unique.  Several boolean fields indicate if a cwt has been
    compromised in some way.
    """

    TAG_TYPE_CHOICES = [
        ("cwt", "Coded Wire Tag"),
        ("sequential", "Sequential Coded Wire Tag"),
    ]

    TAG_MANUFACTURER_CHOICES = [
        ("mm", "Micro Mark"),
        ("nmt", "Northwest Marine Technology"),
    ]

    cwt_number = models.CharField(max_length=6)
    tag_type = models.CharField(max_length=10, choices=TAG_TYPE_CHOICES, default="cwt")

    manufacturer = models.CharField(
        max_length=10, choices=TAG_MANUFACTURER_CHOICES, default="nmt"
    )

    slug = models.CharField(max_length=10, unique=True)

    tag_count = models.IntegerField()
    tag_reused = models.BooleanField(
        "True if this cwt has been stocked by more than one species, strain, or yearclass",
        default=False,
        db_index=True,
    )

    multiple_species = models.BooleanField(
        "True if this cwt has been stocked in more than one species",
        default=False,
        db_index=True,
    )
    multiple_strains = models.BooleanField(
        "True if this cwt has been stocked in more than one strain",
        default=False,
        db_index=True,
    )
    multiple_yearclasses = models.BooleanField(
        "True if this cwt has been stocked in more than one year class",
        default=False,
        db_index=True,
    )
    multiple_makers = models.BooleanField(
        "True if this cwt has been made by more than one tag manufacturer",
        default=False,
        db_index=True,
    )
    multiple_agencies = models.BooleanField(
        "True if this cwt has been stocked by more than one agency",
        default=False,
        db_index=True,
    )
    multiple_lakes = models.BooleanField(
        "True if this cwt has been stocked in more than one lake",
        default=False,
        db_index=True,
    )
    multiple_grid10s = models.BooleanField(
        "True if this cwt has been stocked by more than one 10-minute grid",
        default=False,
        db_index=True,
    )

    class Meta:
        ordering = ["cwt_number"]
        unique_together = ("cwt_number", "manufacturer")

    def save(self, *args, **kwargs):
        """
        Populate slug when we save the object.
        """
        # if not self.slug:
        self.slug = slugify("{}_{}".format(self.cwt_number, self.manufacturer))
        super(CWT, self).save(*args, **kwargs)

    def __str__(self):
        cwt_number = self.cwt_number
        cwt_string = "{}-{}-{}".format(cwt_number[:2], cwt_number[2:4], cwt_number[4:])
        return cwt_string


class CWTsequence(models.Model):
    """
    A model representing a sequence for a CWT object. Most CWTs are not
    sequential and will have a single record in this table with
    seq_start and seq_end both set to 1.  For truly sequential tags,
    seq_start and seq_end will reflect the start and end of the
    series deployed in the associated stocking event(s).
    """

    cwt = models.ForeignKey("CWT", on_delete=models.CASCADE, related_name="cwt_series")

    events = models.ManyToManyField("stocking.StockingEvent", related_name="cwt_series")

    seq_start = models.IntegerField(default=1)
    seq_end = models.IntegerField(default=1)

    class Meta:
        ordering = ["cwt__cwt_number", "seq_start"]

    def __str__(self):
        return "{} [{}-{}]".format(str(self.cwt), self.seq_start, self.seq_end)
