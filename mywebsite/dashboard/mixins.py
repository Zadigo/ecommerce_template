from shop import models

class FormMixin:
    """
    A special mixin created to handle data of m2m fields
    generated by the dynamic fields with Vue JS
    """
    @staticmethod
    def _check_has_same_lengths(*lists):
        """
        Checks whether the incoming arrays
        are all of the same length
        """
        lengths = []
        for item in lists:
            lengths.append(len(item))
        truth_array = []
        count_of_values_test = len(lengths)

        for i in range(count_of_values_test):
            t = i + 1
            if t == count_of_values_test:
                break
            truth_array.append(lengths[t] == lengths[t - 1])
        return all(truth_array)

    @staticmethod
    def _check_if_none(items, index, default=None, constraint=False):
        """
        Checks if an item is none

        Parameters
        ----------

            - items: the actual list of items
            - index: the index of the item to check
            - default: default value if the field is actually none
            - against: 
        """
        try:
            item = items[index]
        except KeyError:
            if constraint and default == None:
                raise exceptions.ValidationError(
                    "La valeur ne peut pas être nul")
            item = default

        return item

    @staticmethod
    def _are_all_image_links(links):
        def conditions(x): return all([
            x.startswith('http'),
            any([
                x.endswith('.jpg'),
                x.endswith('.jpeg'),
                x.endswith('.png')
            ])
        ])
        false_values = list(filterfalse(conditions, links))
        return False if false_values else True, false_values

    def _create_new(self, instance,
                    m2m_field, fields_names: list,
                    model_to_update: type, model_fields: list,
                    should_not_be_none: list = [], defaults: list = [], old_items=None):
        """
        Creates new items in the database using the m2m
        relationship

        Parameters
        -----------

            - unsaved_instance: the current db instance
            - m2m_field: is the name of the m2m field to set
            - fields_names: corresponds to the names of the fields coming from the form
            - model: model in which to create the items
            - model_fields: fields in the model to use for creating the item in the database
        """
        # We will use the first item in the list as our
        # benchmark for testing if we should continue
        # of not with the saving process
        base_field_name_values = self.data.getlist(fields_names[0], [])

        if base_field_name_values:
            field_values = [
                self.data.getlist(field, [])
                for field in fields_names
            ]

            has_same_lengths = self._check_has_same_lengths(*field_values)

            if has_same_lengths:
                list_of_models = [model_to_update for _ in range(
                    len(base_field_name_values))]

                transposed_items = []

                # Transpose to -> [field, [values]]
                for i, values in enumerate(field_values):
                    transposed_items.append([model_fields[i], values])

                final_dict = {}

                for i, model in enumerate(list_of_models):
                    # -> [key, [value1, value2, ...]]
                    for item in transposed_items:
                        key = item[0]
                        value = item[1][i]
                        final_dict.update({key: value})
                    list_of_models[i] = model(**final_dict)
                    final_dict = {}

                transaction.set_autocommit(False)
                try:
                    # with transaction.atomic():
                    # new_items = model_to_update.objects.bulk_create(list_of_models)
                    new_items_primary_keys = []
                    for item in items:
                        item.save()
                        new_items_primary_keys.append(item.pk)
                except:
                    transaction.rollback()
                else:
                    new_items_queryset = model_to_update.objects.filter(
                        id__in=new_items_primary_keys)
                    m2m_relation = getattr(instance, m2m_field)
                    if old_items:
                        new_items_queryset = list(
                            old_items) + list(new_items_queryset)
                    m2m_relation.set(new_items_queryset)
                    return new_items_queryset
                finally:
                    transaction.set_autocommit(True)
        return False

    def _update_old(self, instance, primary_key_name, m2m_field, form_fields: list,
                    model_fields: list, model_to_update: type, cannot_be_none: str = None,
                    default_if_none=None, save=False):
        """
        Updates old items in the database using the m2m relationship

        Parameters
        ----------

            - primary_key_name: name of the field to get the primary keys from
        """
        incoming_values = [
            self.data.getlist(field, [])
            for field in form_fields
        ]

        has_same_lengths = self._check_has_same_lengths(*incoming_values)

        if has_same_lengths:
            incoming_primary_keys = self.data.getlist(primary_key_name, [])
            if incoming_primary_keys:
                queryset = model_to_update.objects.filter(
                    id__in=incoming_primary_keys)

                if queryset.exists():
                    transposed_items = []

                    # Transpose to -> [field, [values]]
                    for i, values in enumerate(incoming_values):
                        transposed_items.append([model_fields[i], values])
                    # raise ValueError()
                    for i, item in enumerate(queryset):
                        for values in transposed_items:
                            setattr(item, values[0], values[1][i])

                    model_to_update.objects.bulk_update(queryset, model_fields)

                    m2m_relation = getattr(instance, m2m_field)
                    m2m_relation.set(queryset)

                    return queryset
        return False

    def _automatic_collections_check(self):
        # Now, check that for automatic collections
        # and see if the product can be included
        # automatic_collections = models.ProductCollection.objects.filter(automatic=True)
        pass

    def _update_old_images(self, product):
        incoming_primary_keys = self.data.getlist('image-key')

        if incoming_primary_keys:
            existing_image_names = self.data.getlist('image-name')
            existing_image_urls = self.data.getlist('image-url', [])
            existing_image_variants = self.data.getlist('image-variant', [])

            all_incoming_images = models.Image.objects.filter(id__in=incoming_primary_keys)
            product_images = product.images.filter(id__in=incoming_primary_keys)

            if product_images.exists():
                for index, image in enumerate(product_images):
                    image.name = existing_image_names[index]
                    image.url = existing_image_urls[index]
                    image.variant = existing_image_variants[index]
                models.Image.objects.bulk_update(product_images, ['name', 'url', 'variant'])

            # product.images.set(product_images)
            product.images.set(all_incoming_images)
            return all_incoming_images
        return False

    def _update_old_variants(self, product):
        product_has_size = self.data.get('has-variant')

        if product_has_size == 'on':
            incoming_primary_keys = self.data.getlist('variant-key')

            if incoming_primary_keys:
                existing_size_names = self.data.getlist('variant')

                existing_verbose_names = self.data.getlist('verbose-name', [])

                product_variants = product.variant.filter(
                    id__in=incoming_primary_keys)
                if product_variants.exists():
                    for index, variant in enumerate(product_variants):
                        variant.name = existing_size_names[index]
                        variant.verbose_name = existing_verbose_names[index]
                    models.Variant.objects.bulk_update(product_variants, ['name', 'verbose_name'])
                    # product.variant.set(product_variants)
                    return product_variants
        return False

    def _create_new_variants(self, product, old_variants=None):
        items = []
        new_variant_names = self.data.getlist('new-variant', [])
        new_verbose_names = self.data.getlist('new-verbose-name')

        if new_variant_names:
            for i in range(len(new_variant_names)):
                try:
                    name = new_variant_names[i]
                except KeyError:
                    name = None

                try:
                    verbose_name = new_verbose_names[i]
                except:
                    verbose_name = None

                if name and verbose_name:
                    items.append(models.Variant(
                        name=name, verbose_name=verbose_name)
                    )

                if name and not verbose_name:
                    items.append(models.Variant(name=name))

            if items:
                new_items_ids = []
                transaction.set_autocommit(False)
                try:
                    for item in items:
                        item.save()
                        new_items_ids.append(item.pk)
                except:
                    transaction.rollback()
                else:
                    transaction.commit()
                    if new_items_ids:
                        new_variants_queryset = models.Variant.objects.filter(
                            id__in=new_items_ids)
                        if old_variants:
                            new_variants_queryset = list(
                                new_variants_queryset) + list(old_variants)
                        product.variant.set(new_variants_queryset)
                finally:
                    transaction.set_autocommit(True)
            return new_variants_queryset
        return False

    def _create_new_images(self, product, old_images=None):
        items = []
        new_image_names = self.data.getlist('new-image-name', [])
        if new_image_names:
            is_not_empty = all(list(map(lambda x: x != '', new_image_names)))

            if is_not_empty is not False:
                new_image_urls = self.data.getlist('new-image-url')
                new_image_variants = self.data.getlist('new-image-variant')
                for i in range(len(new_image_names)):
                    try:
                        name = new_image_names[i]
                    except KeyError:
                        name = None

                    try:
                        url = new_image_urls[i]
                    except:
                        url = None

                    try:
                        variant = new_image_variants[i]
                    except:
                        variant = None

                    if name and url:
                        items.append(models.Image(
                            name=name, url=url, variant=variant))

                if items:
                    new_items_ids = []
                    # transaction.set_autocommit(False)
                    try:
                        for item in items:
                            item.save()
                            new_items_ids.append(item.id)
                    except:
                        pass
                        # transaction.rollback()
                    else:
                        # transaction.commit()
                        if new_items_ids:
                            new_images_queryset = models.Image.objects.filter(
                                id__in=new_items_ids)
                            if old_images:
                                new_images_queryset = list(
                                    new_images_queryset) + list(old_images)
                            product.images.set(new_images_queryset)
                    # transaction.set_autocommit(True)
                return new_images_queryset
        return False