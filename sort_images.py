import random
import numpy as np

from datetime import datetime
from skimage import color #For HSV
from scipy.misc import imsave #For HSV

FRAMES=160
SORT_ALG='combsort'
# bubblesort | cocktailshakersort | heapsort | quicksort | insertionsort | gnomesort | stupidsort | combsort
#SIZE='large' #512x512 from start
SIZE='small' #Start with 16x16

#Dimensions for large and small
LARGE=512
SMALL=16

#TODO - implement more algorithms
#TODO - edit bubblesort and cocktailshakersort not to return seq.  they just sort the damn thing

def main():

  img = shuffled_image()

  max_moves, moves = sort_rows( img )
  print( '{now} Max Moves to Sort: {mm}'.format(now=now(),mm=max_moves) )

  #5 second gif, 24 fps, 120 frames
  #If faster than 32x32 worst-case scenario, record every step
  if max_moves <= 528:
    movie_image_step = 1
  else:
    movie_image_step = max_moves // FRAMES
  frame_number = 0
  
  print( '{now} Applying position swaps to image ...'.format(now=now()) )
  current_move = 0
  while current_move <= max_moves:
    img = apply_swaps( img, moves, current_move )
    #If we're at a save-step
    if current_move % movie_image_step == 0:
      frame_number = save_image( img, frame_number )
    current_move += 1

def now():
  return datetime.now().strftime( '%Y/%m/%d %H:%M:%S' )

def shuffled_image():
  if SIZE == 'large':
    dim=LARGE
  elif SIZE == 'small':
    dim=SMALL
  #Create image, set colors, shuffle
  print( '{now} Creating image ...'.format(now=now()) )
  img = np.zeros((dim,dim,3), dtype='float32')
  print( '{now}  ... setting colors'.format(now=now()) )
  for i in range(img.shape[1]):
    img[:,i,:] = i / img.shape[1], 1.0, 1.0
  print( '{now}  ... shuffling rows'.format(now=now())  )
  for i in range(img.shape[0]):
    np.random.shuffle( img[i,:,:] )
  return img
  
def sort_rows( img ):
  moves = []
  max_moves = 0
  print( '{now} Sorting rows ...'.format(now=now()) )
  for i in range(img.shape[0]):
    print( list(img[i,:,0]) )
    _, rowsort = sort( list(img[i,:,0]) )
    moves.append(rowsort)
    if len( rowsort ) > max_moves:
      max_moves = len(rowsort)
  return max_moves, moves

def save_image( img, frame_num ):
  print( '{now}  ... saving frame {num}.png'.format(now=now(), num=str(frame_num).zfill(3)) )
  saveimg = expand_image( img )  #If small, is expanded
  imsave( '{dir}/{fn}.png'.format(dir=SORT_ALG, fn=str(frame_num).zfill(3)), color.convert_colorspace(saveimg, 'HSV', 'RGB') )
  return frame_num + 1

def apply_swaps( img, moves, current_move ):
  for i in range(img.shape[0]):
    if current_move < len(moves[i]):
      img = swap_pixels(i, moves[i][current_move], img )
  return img

  return seq, swaps

#To sort columns
#Row is constant
#Places is an entry from swaps[] generated by bubblesort
def swap_pixels( row, places, img ):
  tmp = img[row,places[0],:].copy() #A single pixel
  img[row,places[0],:] = img[row,places[1],:]
  img[row,places[1],:] = tmp
  return img

#Turns 32x32 into 512x512 (16 times larger)
def expand_image( img ):
  #Not creating a monster image
  if img.shape[0] > 32:
    return img
  print( '{now}  ... expanding image for large square pixels'.format(now=now()) )
  newimg = np.zeros((16*img.shape[0],16*img.shape[1],3), dtype='float32')
  for i in range(img.shape[0]):   #Row
    for j in range(img.shape[1]): #Col
      for x in range(16*i, 16*i+16):   #new_row
        for y in range(16*j, 16*j+16): #new_col
          newimg[x][y] = img[i][j]
  return newimg


def sort( seq ): #To swap algorithms
  if SORT_ALG == 'bubblesort':
    return bubblesort( seq )
  elif SORT_ALG == 'cocktailshakersort':
    return cocktailshakersort( seq )
  elif SORT_ALG == 'insertionsort':
    return 'lolno', insertionsort( seq )
  elif SORT_ALG == 'stupidsort' or SORT_ALG == 'gnomesort':
    return 'lolno', stupidsort( seq )
  elif SORT_ALG == 'heapsort':
    return 'lolno', heapsort( seq )
  elif SORT_ALG == 'quicksort':
    swaps = []
    return 'lolno', quicksort( seq, 0, len(seq)-1, swaps )
  elif SORT_ALG == 'mergesort':
    swaps = []
    return 'lolno', mergesort( seq, 0, len(seq), swaps )
  elif SORT_ALG == 'combsort':
    return 'lolno', combsort( seq )

#Need to record each position swap as well
#Moves smallest to the left, progressively 
#stops checking lowest as goes
def bubblesort( seq ):
  swaps = []
  for x in range(len(seq)):
    for y in range(len(seq)-1,x,-1):
      if seq[y] < seq[y-1]:
        swaps.append([y, y-1])
        tmp = seq[y]
        seq[y] = seq[y-1]
        seq[y-1] = tmp
  return seq, swaps

def cocktailshakersort( seq ):
  swaps = []
  #Determined by testing cause I'm lazy
  largest = len(seq) - 1 #adjust indices for lists
  smallest = 0
  while True:
    #Sort up.
    for x in range( smallest, largest ):
      if seq[x] > seq[x+1]:
        swaps.append([x,x+1])
        temp = seq[x]
        seq[x] = seq[x+1]
        seq[x+1] = temp
    #Adjust end
    largest -= 1
    if largest <= smallest:
      break

    #Sort down.  
    for x in range( largest, smallest, -1 ):
      if seq[x] < seq[x-1]:
        swaps.append([x,x-1])
        temp = seq[x]
        seq[x] = seq[x-1]
        seq[x-1] = temp
    #Adjust start
    smallest += 1
    if largest <= smallest:
      break
    
  return seq, swaps

def heapsort( seq ):
  swaps = []
  length = len(seq)
  
  #Everything in order when gets to next set
  for x in range(length, -1, -1):
    build_heap( seq, length, x, swaps )

  for x in range(length-1, 0, -1):
    swaps.append( [0,x] )
    tmp = seq[0]
    seq[0] = seq[x]
    seq[x] = tmp

    #Leaving end alone, make re-heap everything
    build_heap( seq, x, 0, swaps ) 

  return swaps

def build_heap( seq, siz, root, swaps ):
  #track largest
  largest = root

  #check for right and left children
  left = 2*largest + 1
  right = 2*largest + 2

  #if exist and larger, swap 
  if left < siz and seq[left] > seq[largest]:
    largest = left
  if right < siz and seq[right] > seq[largest]:
    largest = right

  if root != largest:
    swaps.append([root,largest])
    temp = seq[root]
    seq[root] = seq[largest]
    seq[largest] = temp 
    #Recursively make sure all leaves follow heap property
    build_heap( seq, siz, largest, swaps )

#Hoare Algorithm, random pivots
def quicksort( seq, low, high, swaps ):
  if low < high:
    sep, swaps = hor_partition( seq, low, high, swaps )  
    # Separation not exactly in right spot, must keep sorting those same spots
    swaps = quicksort( seq, low, sep, swaps )
    swaps = quicksort( seq, sep+1, high, swaps )
  return swaps

def hor_partition( seq, low, high, swaps ):
  pivot = seq[random.randint(low,high)]
  low_index = low 
  high_index = high  
  while True:
    while seq[high_index] > pivot:
      high_index -= 1
    while seq[low_index] < pivot:
      low_index += 1
    if low_index < high_index:
      swaps.append( [low_index, high_index] )
      seq[high_index],seq[low_index] = seq[low_index],seq[high_index]
      high_index -= 1
      low_index += 1
    else:
      return high_index, swaps

def insertionsort( seq ):
  swaps = []
  for x in range( 1, len(seq) ):
    for y in range(x, 0, -1):
      if seq[y] < seq[y-1]:
        swaps.append( [y,y-1] )
        seq[y],seq[y-1] = seq[y-1],seq[y]
  return swaps

def stupidsort( seq ):
  x = 0
  swaps = []
  while x < len(seq):
    if x == 0:
      x += 1
    elif seq[x] >= seq[x-1]:
      x += 1
    else:
      sorts.append([x,x-1])
      seq[x],seq[x-1] = seq[x-1],seq[x]
      x -= 1
  return swaps

def combsort( seq ):
  swaps = []
  size = len(seq)
  gap = len(seq)
  shrink = 1.3
  complete = False

  while not complete:
    gap = int(gap/shrink)
    if gap <= 1:
      gap = 1
      complete = True #Turned false if any swaps happen
  
    index = 0
    while index + gap < size:
      if seq[index] > seq[index+gap]:
        swaps.append([index,index+gap])
        seq[index],seq[index+gap]=seq[index+gap],seq[index]
        complete = False
      index += 1
  return swaps

if __name__ == '__main__':
  main()
