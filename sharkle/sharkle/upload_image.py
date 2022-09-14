import os
from random import randint
from django.utils.timezone import now

def upload_image(instance, filename):
  filename_base, filename_ext = os.path.splitext(filename)

  return ('%s' % (
      #instance.id,
      now().strftime('%Y%m%d')+'_'+str(randint(10000000,99999999))
  ))+filename_ext
